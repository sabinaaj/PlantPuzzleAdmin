from django.views.generic import View, CreateView, UpdateView, ListView, DeleteView
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from visitors.models import SchoolGroup
from areas.models import Area
from .forms import WorksheetForm
from .models import Worksheet, TaskType, Task, Question, Option, TaskImage
from .serializers import WorksheetsSerializer, WorksheetSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import re
import logging

logger = logging.getLogger(__name__)


class WorksheetListView(LoginRequiredMixin, ListView):
    model = Worksheet
    template_name = 'worksheets_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['area'] = self.area
        context['worksheets'] = Worksheet.objects.filter(area=self.area)

        return context


class BaseWorksheetView(LoginRequiredMixin):
    template_name = 'worksheets_form.html'
    form_class = WorksheetForm
    model = Worksheet

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['area'] = self.area
        context['school_groups'] = SchoolGroup.objects.all()
        context['task_types'] = TaskType.objects.all()

        return context

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Formulář obsahuje chyby, prosím opravte je a zkuste znovu.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('worksheets:worksheets_list', kwargs={'area': self.area.pk})

    def create_type_1_task(self, request, task_num):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.TWO_CHOICES),
            text=request.POST.get(f'task-{task_num}-text')
        )

        option_text_0 = request.POST.get(f'option_{task_num}-0-text')
        option_text_1 = request.POST.get(f'option_{task_num}-1-text')

        questions = {k:v for (k, v) in request.POST.items() if k.startswith(f'question_{task_num}') and k.endswith('text')}
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

        if image:
            task = Task.objects.create(
                worksheet=self.worksheet,
                type=TaskType.objects.get(type=TaskType.Type.CHOICES_PICTURE),
                text=request.POST.get(f'task-{task_num}-text'),
            )

            image_src = request.FILES.get(f'{task_num}-image')
            if image_src:
                TaskImage.objects.create(
                    task=task,
                    image=image_src
                )
            if not image_src:
                image_pk = request.POST.get(f'{task_num}-image-original')
                image = TaskImage.objects.get(pk=image_pk)

                image.task = task
                image.save()

            question = Question.objects.create(
                task=task
            )

        else:
            task = Task.objects.create(
                worksheet=self.worksheet,
                type=TaskType.objects.get(type=TaskType.Type.CHOICES),
                text=request.POST.get(f'task-{task_num}-text')
            )

            question = Question.objects.create(
                task=task,
                text=request.POST.get(f'question_{task_num}-text')
            )

        options = {k:v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('text')}

        for option_name, option_text in options.items():
            option_num = re.findall(r'\d+', option_name)[1]
            is_correct = True if request.POST.get(f'option_{task_num}-{option_num}-is_correct') else False

            Option.objects.create(
                question=question,
                text=option_text,
                is_correct=is_correct
            )

    def create_type_4_task(self, request, task_num):

        task = Task.objects.create(
            worksheet=self.worksheet,
            type=TaskType.objects.get(type=TaskType.Type.MULTIPLE_CHOICES_PICTURE),
            text=request.POST.get(f'task-{task_num}-text'),
        )

        image_src = request.FILES.get(f'{task_num}-image')
        if image_src:
            TaskImage.objects.create(
                task=task,
                image=image_src
            )
        if not image_src:
            image_pk = request.POST.get(f'{task_num}-image-original')
            image = TaskImage.objects.get(pk=image_pk)

            image.task = task
            image.save()

        options = [v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('text')]
        options_correct = [v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('is_correct')]

        for i, correct_option in enumerate(options_correct):
            if not correct_option:
                continue

            question = Question.objects.create(
                task=task,
                text=correct_option
            )

            for j, option in enumerate(options):
                # Correct if number of correct answer is same as number of option
                is_correct = option == options[i]

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

        questions = {k: v for (k, v) in request.POST.items() if k.startswith(f'question_{task_num}') and k.endswith('text')}
        options = {k:v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('text')}

        for question_name, question_text in questions.items():
            question_num = re.findall(r'\d+', question_name)[1]

            question = Question.objects.create(
                task=task,
                text=question_text
            )

            for option_name, option_text in options.items():
                is_correct = True if option_name==('option_'+task_num+'-'+question_num+'-text') else False

                Option.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=is_correct
                )


class WorksheetCreateView(BaseWorksheetView, CreateView):

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.instance.area = self.area
        self.object = None

        if not form.is_valid():
            return self.form_invalid(form)

        self.worksheet = form.save()

        school_group_ids = request.POST.getlist('school_group')
        self.worksheet.school_groups.set(school_group_ids)
        self.worksheet.save()

        tasks = {k: v for (k, v) in request.POST.items() if k.startswith('task') and k.endswith('type')}

        for task_type, value in tasks.items():
            task_num = re.findall(r'\d+', task_type)[0]

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['worksheet'] = None
        context['tasks_data'] = None
        context['selected_school_groups'] = None

        return context


class WorksheetUpdateView(BaseWorksheetView, UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        worksheet = self.get_object()

        context['tasks_data'] = [
            {
                'type': task.type.id,
                'text': task.text or '',
                'imagePk': task.taskimage_set.first().pk if task.taskimage_set.exists() else '',
                'imageUrl': task.taskimage_set.first().image.url if task.taskimage_set.exists() else '',
                'questions': self.prepare_task_data(task),
            }
            for task in worksheet.task_set.all()
        ]

        context['selected_school_groups'] = list(worksheet.school_groups.all().values_list('pk', flat=True))

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.instance.area = self.area

        self.worksheet = self.get_object()
        form.instance = self.worksheet

        if not form.is_valid():
            return self.form_invalid(form)

        form.save()

        school_group_ids = request.POST.getlist('school_group')
        self.worksheet.school_groups.set(school_group_ids)
        self.worksheet.save()

        # delete all tasks
        self.worksheet.task_set.all().delete()

        tasks = {k: v for (k, v) in request.POST.items() if k.startswith('task') and k.endswith('type')}

        for task_type, value in tasks.items():
            task_num = re.findall(r'\d+', task_type)[0]

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

        # Delete unused images
        TaskImage.objects.filter(image__isnull=True).delete()

        return super().post(request, *args, **kwargs)

    def prepare_task_data(self, task):

        if task.type.id == 1:
            questions = self.prepare_type_1_task_data(task)
        elif task.type.id == 2:
            questions = self.prepare_type_2_or_3_task_data(task)
        elif task.type.id == 3:
            questions = self.prepare_type_2_or_3_task_data(task)
        elif task.type.id == 4:
            questions = self.prepare_type_4_task_data(task)
        elif task.type.id == 5:
            questions = self.prepare_type_5_task_data(task)

        return questions if questions else []


    def prepare_type_1_task_data(self, task):
        questions = task.question_set.all()
        options = questions[0].option_set.all() if questions else []

        return {
            'rows': questions.count(),
            'options': [option.text if option.text else "" for option in options],
            'questions': [
                {
                    'text': question.text if question.text else "",
                    'correct': 0 if question.option_set.first().is_correct else 1,
                }
                for question in questions
            ],
        }

    def prepare_type_2_or_3_task_data(self, task):
        question = task.question_set.first()
        options = question.option_set.all() if question else []

        return {
            'rows': options.count(),
            'question': question.text if question.text else '',
            'options': [
                {'text': option.text if option.text else '',
                 'correct': 'on' if option.is_correct else ''}
                for option in options
            ],
        }

    def prepare_type_4_task_data(self, task):

        questions = task.question_set.all()
        options = questions[0].option_set.all() if questions else []

        correct_answers = []
        for question in questions:
            correct_option = question.option_set.filter(is_correct=True).first()

            if correct_option:
                correct_option = correct_option.text

            correct_answers.append((question.text, correct_option))

        return {
            'rows': options.count() if options else 0,
            'questions': task.question_set.count(),
            'options': [
                {
                    'text': option.text if option.text else '',
                    'correct': [answer[0] for answer in correct_answers if answer[1] == option.text],
                }
                for option in options
            ],
        }

    def prepare_type_5_task_data(self, task):
        questions = task.question_set.all()

        return {
            'rows': questions.count(),
            'questions': [
                {
                    'text': question.text if question.text else '',
                    'correct': question.option_set.filter(is_correct=True).first().text
                    if question.option_set.filter(is_correct=True).exists()
                    else '',
                }
                for question in questions
            ],
        }


class LoadTaskFormView(View):
    template_mapping = {
        '1': 'task_type_1.html',
        '2': 'task_type_2.html',
        '3': 'task_type_3.html',
        '4': 'task_type_4.html',
        '5': 'task_type_5.html',
    }

    def get(self, request, *args, **kwargs):
        task_type = kwargs.get('task_type')
        template_name = self.template_mapping.get(task_type)

        if template_name:
            html_content = render_to_string(template_name, request=request)
            return JsonResponse({'html': html_content})
        else:
            return JsonResponse({'error': 'Invalid task type'}, status=400)


class CheckFormDataAjaxView(View):

    errors = {}

    def post(self, request, *args, **kwargs):
        self.errors = {}
        title = request.POST.get('title')

        if not title:
            self.errors['title'] = "Název je povinný."
        else:
            if len(title) > 50:
                self.errors['title'] = 'Název může mít max. 50 znaků.'

            worksheet_pk = request.POST.get('worksheet_pk')
            if worksheet_pk:
                if Worksheet.objects.exclude(pk=worksheet_pk).filter(title=title).exists():
                    self.errors['title'] = 'Pracovní list s tímto názvem již existuje.'
            else:
                if Worksheet.objects.filter(title=title).exists():
                    self.errors['title'] = 'Pracovní list s tímto názvem již existuje.'


        tasks = {k: v for (k, v) in request.POST.items() if k.startswith('task') and k.endswith('type')}

        images = {k: v for (k, v) in request.POST.items() if k.endswith('image')}
        for image_name, image in images.items():
            task_num = re.findall(r'\d+', image_name)[0]
            image = image or request.POST.get(f'{task_num}-image-original')

            if not image:
                self.errors[image_name] = 'Obrázek je povinný.'


        questions = {k: v for (k, v) in request.POST.items() if k.startswith('question') and k.endswith('text')}
        for question_name, question in questions.items():
            if not question:
                self.errors[question_name] = 'Toto pole je povinné.'
            elif len(question) >= 100:
                self.errors[question_name] = f'Maximální počet znaků je 150. Máte {len(question)}.'

        options = {k:v for (k, v) in request.POST.items() if k.startswith('option') and k.endswith('text')}
        for option_name, option in options.items():
            if not option:
                self.errors[option_name] = 'Toto pole je povinné.'
            elif len(option) >= 50:
                self.errors[option_name] = f'Maximální počet znaků je 50. Máte {len(option)}.'


        for task_type, value in tasks.items():
            task_num = re.findall(r'\d+', task_type)[0]

            task_text = request.POST.get(f'task-{task_num}-text')
            if not task_text:
                self.errors[f'task-{task_num}-text'] = 'Zadání je povinné.'
            elif len(task_text) >= 150:
                self.errors[f'task-{task_num}-text'] = f'Maximální počet znaků je 150. Máte {len(task_text)}.'

            elif value == '2':
                self.check_type_2_or_3_task_data(request, task_num)
            elif value == '3':
                self.check_type_2_or_3_task_data(request, task_num)
            elif value == '4':
                self.check_type_4_task_data(request, task_num)

        if self.errors:
            return JsonResponse({'status': False, 'errors': self.errors})

        return JsonResponse({'status': True})


    def check_type_2_or_3_task_data(self, request, task_num):

        options_checkboxes = {k: v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('-is_correct')}

        if not options_checkboxes:
            self.errors[f'checkbox-{task_num}'] = 'Vyberte správnou odpověď.'


    def check_type_4_task_data(self, request, task_num):
        counter_value = request.POST.get(f'question_{task_num}-counter')

        if not counter_value.isdigit():
            self.errors[f'question_{task_num}-counter'] = 'Toto pole musí obsahovat číslo.'

        else:
            counter_value = int(counter_value)
            if not (1 <= counter_value <= 15):
                self.errors[f'question_{task_num}-counter'] = 'Číslo musí být v rozmezí od 1 do 15.'

        options_correct_raw = [v for (k, v) in request.POST.items() if k.startswith(f'option_{task_num}') and k.endswith('is_correct')]
        options_correct = []

        for value in options_correct_raw:
            if value.isdigit():
                options_correct.append(int(value))

        if len(options_correct) != counter_value:
            self.errors[f'select-{task_num}'] = 'Musíte použít všechna čísla.'

        if len(options_correct) != len(set(options_correct)):
            self.errors[f'select-{task_num}'] = 'Každé číslo může být použito pouze jednou.'


class WorksheetDeleteView(LoginRequiredMixin, DeleteView):
    model = Worksheet

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('worksheets:worksheets_list', kwargs={'area': self.area.pk})


class WorksheetsByAreaAPIView(APIView):

    def get(self, request, area_id):
        worksheets = Worksheet.objects.filter(area_id=area_id)
        if not worksheets.exists():
            return Response({"detail": "No worksheets found for this area."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorksheetsSerializer(worksheets, many=True)
        return Response(serializer.data)


class WorksheetAPIView(APIView):

    def get(self, request, worksheet_id):
        worksheet = Worksheet.objects.filter(pk=worksheet_id).first()
        if not worksheet:
            return Response({"detail": "No worksheet found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorksheetSerializer(worksheet, context={'request': request})
        return Response(serializer.data)
