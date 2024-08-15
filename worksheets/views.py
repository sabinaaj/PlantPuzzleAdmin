from django.views.generic import View, CreateView, ListView
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse, HttpResponseRedirect
from django.forms import inlineformset_factory

from visitors.models import SchoolGroup
from areas.models import Area
from .forms import WorksheetForm, TaskForm, QuestionForm, OptionForm
from .models import Worksheet, TaskType, Task, Question, Option

import re
import logging
logger = logging.getLogger(__name__)


class WorksheetListView(ListView):
    model = Worksheet
    template_name = "worksheets_list.html"

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs["area"])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["area"] = self.area
        context["worksheets"] = Worksheet.objects.filter(area=self.area)

        return context


class WorksheetCreateView(CreateView):
    template_name = "worksheets_form.html"
    form_class = WorksheetForm
    model = Worksheet

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs["area"])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["school_groups"] = SchoolGroup.objects.all()
        context["task_types"] = TaskType.objects.all()

        TaskFormSet = inlineformset_factory(Worksheet, Task, form=TaskForm, extra=1, can_delete=True)
        context["task_formset"] = TaskFormSet(prefix='tasks')

        QuestionFormSet = inlineformset_factory(Task, Question, form=QuestionForm, extra=1, can_delete=True)
        context["question_formset"] = QuestionFormSet(prefix='questions')

        OptionFormSet = inlineformset_factory(Question, Option, form=OptionForm, extra=1, can_delete=True)
        context["option_formset"] = OptionFormSet(prefix='options')

        return context

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.instance.area = self.area

        if not form.is_valid():
            return self.form_invalid(form)

        self.worksheet = form.save()

        logger.warning("post: %s", request.POST)

        tasks = {k:v for (k, v) in request.POST.items() if k.startswith('task') and k.endswith('type')}
        logger.warning("tasks: %s", tasks)

        for task_type, value in tasks.items():
            task_num =re.findall(r'\d+', task_type)[0]

            if value == '1':
                self.create_type_1_task(request, task_num)
            elif value == '2':
                self.create_type_2_or_3_task(request, task_num)
            elif value == '3':
                self.create_type_2_or_3_task(request, task_num, image=True)
            elif value == '4':
                self.create_type_4_task(request, task_num)
            elif value == '5':
                self.create_type_5_task(request, task_num)


        return super().post(request, *args, **kwargs)

    def create_type_1_task(self, request, task_num):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.TWO_CHOICES),
            text=request.POST.get(f'task-{task_num}-text')
        )

        option_text_0 = request.POST.get(f'option_{task_num}-0-text')
        option_text_1 = request.POST.get(f'option_{task_num}-1-text')

        questions = {k:v for (k, v) in request.POST.items() if k.startswith(f"question_{task_num}") and k.endswith('text')}
        for question_name, question_text in questions.items():

            question_num = re.findall(r'\d+', question_name)[1]

            question = Question.objects.create(
                task=task,
                text=question_text
            )

            is_correct_0 = request.POST.get(f'option_{task_num}-{question_num}-is_correct') == 'is_correct_0'

            Option.objects.bulk_create([
                Option(question=question, text=option_text_0, is_correct=is_correct_0),
                Option(question=question, text=option_text_1, is_correct=not is_correct_0)
            ])

    def create_type_2_or_3_task(self, request, task_num, image=False):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.CHOICES),
            text=request.POST.get(f'task-{task_num}-text')
        )

        if image:
            question = Question.objects.create(
                task=task,
                text=request.POST.get(f'question_{task_num}-text')
            )
        else:
            question = Question.objects.create(
                task=task,
                image=request.FILES.get(f'question_{task_num}-image')
            )

        options = {k:v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('text')}

        for option_name, option_text in options.items():
            option_num = re.findall(r'\d+', option_name)[1]

            Option.objects.create(
                question=question,
                text=option_text,
                is_correct=request.POST.get(f'option_{task_num}-{option_num}-is_correct')
            )

    def create_type_4_task(self, request, task_num):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.MULTIPLE_CHOICES_PICTURE),
            text=request.POST.get(f'task-{task_num}-text')
        )

        options = [v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('text')]
        options_correct = [v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('is_correct')]

        question_num = int(request.POST.get(f'question_{task_num}-counter'))
        for i in range(question_num):
            question = Question.objects.create(
                task=task,
                image=request.FILES.get(f'question_{task_num}-image')
            )

            for j, option in enumerate(options):
                is_correct = int(options_correct[i]) == (j + 1)

                Option.objects.create(
                    question=question,
                    text=option,
                    is_correct=is_correct
                )

    def create_type_5_task(self, request, task_num):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.PAIRS),
            text=request.POST.get(f'task-{task_num}-text')
        )

        questions = {k: v for (k, v) in request.POST.items() if k.startswith(f"question_{task_num}") and k.endswith('text')}
        options = {k:v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('text')}

        for question_name, question_text in questions.items():
            question_num = re.findall(r'\d+', question_name)[1]

            question = Question.objects.create(
                task=task,
                text=question_text
            )

            for option_name, option_text in options.items():
                logger.warning("question: %s %s", option_name, 'option_'+task_num+'-'+question_num+'-text')
                is_correct = True if option_name==('option_'+task_num+'-'+question_num+'-text') else False

                Option.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=is_correct
                )





    def get_success_url(self):
        return reverse("worksheets:worksheets_list", kwargs={"area": self.area.pk})


class LoadTaskFormView(View):
    template_mapping = {
        "1": "task_type_1.html",
        "2": "task_type_2.html",
        "3": "task_type_3.html",
        "4": "task_type_4.html",
        "5": "task_type_5.html",
    }

    def get(self, request, *args, **kwargs):
        task_type = kwargs.get('task_type')
        template_name = self.template_mapping.get(task_type)

        if template_name:
            html_content = render_to_string(template_name, request=request)
            return JsonResponse({'html': html_content})
        else:
            return JsonResponse({'error': 'Invalid task type'}, status=400)

