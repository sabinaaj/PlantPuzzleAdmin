from django.views.generic import View, CreateView, ListView
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.forms import inlineformset_factory

from visitors.models import SchoolGroup
from areas.models import Area
from .forms import WorksheetForm, TaskForm, QuestionForm, OptionForm
from .models import Worksheet, TaskType, Task, Question, Option


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
        form.instance.area = self.area

        TaskFormSet = inlineformset_factory(Worksheet, Task, form=TaskForm, extra=1, can_delete=True)
        task_formset = TaskFormSet(self.request.POST, prefix='tasks')
        if task_formset.is_valid():
            self.object = form.save()
            tasks = task_formset.save(commit=False)
            for task in tasks:
                task.worksheet = self.object
                task.save()

                QuestionFormSet = inlineformset_factory(Task, Question, form=QuestionForm, extra=1, can_delete=True)
                question_formset = QuestionFormSet(self.request.POST, prefix=f'questions_{task.id}')
                if question_formset.is_valid():
                    questions = question_formset.save(commit=False)
                    for question in questions:
                        question.task = task
                        question.save()

                        OptionFormSet = inlineformset_factory(Question, Option, form=OptionForm, extra=1, can_delete=True)
                        option_formset = OptionFormSet(self.request.POST, prefix=f'options_{question.id}')
                        if option_formset.is_valid():
                            options = option_formset.save(commit=False)
                            for option in options:
                                option.question = question
                                option.save()
            return super().form_valid(form)

        else:
            return self.form_invalid(form)


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

