from django.views.generic import View, CreateView, ListView, DeleteView
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, reverse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from openpyxl import Workbook, utils as OpenPyXlUtils
from openpyxl.styles import Alignment, Font, Border, Side
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
from openpyxl.drawing.image import Image
from tempfile import NamedTemporaryFile
from random import shuffle

from visitors.models import SchoolGroup
from areas.models import Area
from .forms import WorksheetForm
from .models import Worksheet, TaskType, Task, Question, Option

import os
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

        context["area"] = self.area
        context["school_groups"] = SchoolGroup.objects.all()
        context["task_types"] = TaskType.objects.all()

        return context

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
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

        if image:
            task = Task.objects.create(
                worksheet=self.worksheet,
                type=TaskType.objects.get(type=TaskType.Type.CHOICES_PICTURE),
                text=request.POST.get(f'task-{task_num}-text'),
                image=request.FILES.get(f'question_{task_num}-image')
            )

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

        options = {k:v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('text')}

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
            image=request.FILES.get(f'question_{task_num}-image')
        )

        options = [v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('text')]
        options_correct = [v for (k, v) in request.POST.items() if k.startswith(f"option_{task_num}") and k.endswith('is_correct')]

        question_cnt = int(request.POST.get(f'question_{task_num}-counter'))
        for i in range(question_cnt):
            question = Question.objects.create(
                task=task,
                text=i+1
            )

            for j, option in enumerate(options):
                # Correct if number of correct answer is same as number of option
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


class WorksheetDeleteView(DeleteView):
    model = Worksheet

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs["area"])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("worksheets:worksheets_list", kwargs={"area": self.area.pk})



class BaseWorksheetExportView(View):

    worksheet = None
    sheet = None
    row_cnt = 0

    def dispatch(self, request, *args, **kwargs):
        self.worksheet = get_object_or_404(Worksheet, pk=kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def change_column_width(self, column_widths):
        for i, width in enumerate(column_widths):
            column_letter = OpenPyXlUtils.get_column_letter(i + 1)
            self.sheet.column_dimensions[column_letter].width = width

    def make_header(self):
        self.sheet.merge_cells('A1:O3')
        self.sheet['A1'] = self.worksheet.title
        self.sheet['A1'].font = Font(name='Calibri', bold=True, size=20)
        self.sheet['A1'].alignment = Alignment(horizontal='center', vertical='center')

        self.row_cnt += 5

    def make_task_text(self, task_num, text):
        self.sheet.merge_cells(f'A{self.row_cnt}:O{self.row_cnt}')
        self.sheet[f'A{self.row_cnt}'] = f'{task_num}. {text}'
        self.sheet[f'A{self.row_cnt}'].font = Font(name='Calibri', bold=True)
        self.row_cnt += 2

    def prepare_image_for_cell(self, img_path, col):
        img = Image(img_path)

        cell_width = 99200
        cell_height = 75600

        offset_x = int((cell_width - cell_height) / 2)
        offset_y = 0

        _from = AnchorMarker(col=col, row=self.row_cnt - 1, colOff=offset_x, rowOff=offset_y)
        to = AnchorMarker(col=col + 1, row=self.row_cnt, colOff=-offset_x, rowOff=-offset_y)
        img.anchor = TwoCellAnchor(editAs="twoCell", _from=_from, to=to)

        return img

    def post(self, request, **kwargs):

        workbook = Workbook()
        self.sheet = workbook.active

        column_widths = [3, 3, 3, 9, 6, 6, 3, 3, 6, 3, 9, 3, 9, 3, 3]
        self.change_column_width(column_widths)

        self.make_header()

        tasks = self.worksheet.task_set.all()
        for task_num, task in enumerate(tasks):
            self.make_task_text(task_num + 1, task.text)

            if task.type.type == TaskType.Type.TWO_CHOICES:
                self.make_two_choices_task(task)

            elif task.type.type == TaskType.Type.CHOICES:
                self.make_choices_task(task)

            elif task.type.type == TaskType.Type.CHOICES_PICTURE:
                self.make_choices_picture_task(task)

            elif task.type.type == TaskType.Type.MULTIPLE_CHOICES_PICTURE:
                self.make_multiple_choices_picture_task(task)

            elif task.type.type == TaskType.Type.PAIRS:
                self.make_pairs_task(task)


            self.row_cnt += 2


        self.row_cnt += 1

        with NamedTemporaryFile() as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()

        response = HttpResponse(content=stream, content_type="application/ms-excel", )
        response["Access-Control-Expose-Headers"] = f"Content-Disposition"
        response["Content-Disposition"] = f"attachment; filename=pracovni_list.xlsx"
        return response


@method_decorator(csrf_exempt, name="dispatch")
class WorksheetExportView(BaseWorksheetExportView):

    def make_two_choices_task(self, task):

        questions = task.question_set.all()
        options = questions[0].option_set.all() if len(questions) else []

        self.sheet.merge_cells(f'F{self.row_cnt}:J{self.row_cnt}')
        self.sheet[f'F{self.row_cnt}'] = options[0].text
        self.sheet[f'F{self.row_cnt}'].alignment = Alignment(horizontal='center')

        self.sheet.merge_cells(f'K{self.row_cnt}:M{self.row_cnt}')
        self.sheet[f'K{self.row_cnt}'] = options[1].text
        self.sheet[f'K{self.row_cnt}'].alignment = Alignment(horizontal='center')
        self.row_cnt += 1

        self.sheet.row_dimensions[self.row_cnt].height = 10
        self.row_cnt += 1

        img_path = os.path.join(settings.STATIC_ROOT, 'box.jpeg')

        for question in questions:
            self.sheet.merge_cells(f'B{self.row_cnt}:E{self.row_cnt}')
            self.sheet[f'B{self.row_cnt}'] = question.text

            box_1 = self.prepare_image_for_cell(img_path, col=7)
            box_2 = self.prepare_image_for_cell(img_path, col=11)

            self.sheet.add_image(box_1)
            self.sheet.add_image(box_2)

            self.row_cnt += 1
            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1

    def make_choices_task(self, task):

        questions = task.question_set.all()

        for question in questions:
            self.sheet.merge_cells(f'B{self.row_cnt}:O{self.row_cnt}')
            self.sheet[f'B{self.row_cnt}'] = question.text
            self.row_cnt += 1

            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1

            char = ord('a')
            for option in question.option_set.all():
                self.sheet[f'C{self.row_cnt}'] = f'{chr(char)})'
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='center')
                char += 1

                self.sheet.merge_cells(f'D{self.row_cnt}:O{self.row_cnt}')
                self.sheet[f'D{self.row_cnt}'] = option.text
                self.row_cnt += 1

                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1


    def make_choices_picture_task(self, task):

        question = task.question_set.first()

        self.sheet.merge_cells(f'C{self.row_cnt}:M{self.row_cnt + 5}')
        self.row_cnt += 7
        char = ord('a')
        for option in question.option_set.all():
            self.sheet.merge_cells(f'E{self.row_cnt}:M{self.row_cnt}')
            self.sheet[f'E{self.row_cnt}'] = f'{chr(char)}) {option.text}'
            self.row_cnt += 1
            char += 1

            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1



    def make_multiple_choices_picture_task(self, task):

        question = task.question_set.first()

        self.sheet.merge_cells(f'C{self.row_cnt}:M{self.row_cnt + 5}')
        self.row_cnt += 7

        self.sheet.merge_cells(f'A{self.row_cnt}:O{self.row_cnt}')
        all_options = [option.text for option in question.option_set.all()]
        self.sheet[f'A{self.row_cnt}'] = f'Výběr pojmů: {", ".join(all_options)}'
        self.row_cnt += 3

        for i in range(len(all_options)):

            if i % 2 == 0:
                self.sheet[f'C{self.row_cnt}'] = f'{i + 1}.  '
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='right')

                for col in ['D', 'E', 'F', 'G']:
                    self.sheet[f'{col}{self.row_cnt}'].border = Border(bottom=Side(style='thin'))

            else:
                self.sheet[f'I{self.row_cnt}'] = f'{i + 1}.  '
                self.sheet[f'I{self.row_cnt}'].alignment = Alignment(horizontal='right')

                for col in ['J', 'K', 'L', 'M']:
                    self.sheet[f'{col}{self.row_cnt}'].border = Border(bottom=Side(style='thin'))
                self.row_cnt += 1


                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1

        self.row_cnt += 1


    def make_pairs_task(self, task):

            questions = task.question_set.all()
            options = list(questions[0].option_set.all() if len(questions) else [])

            shuffle(options)

            for i, question in enumerate(questions):
                self.sheet.merge_cells(f'C{self.row_cnt}:F{self.row_cnt}')
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'C{self.row_cnt}'] = question.text

                self.sheet.merge_cells(f'J{self.row_cnt}:M{self.row_cnt}')
                self.sheet[f'J{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'J{self.row_cnt}'] = options[i].text

                self.row_cnt += 1

                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1



@method_decorator(csrf_exempt, name="dispatch")
class WorksheetExportWithAnswersView(BaseWorksheetExportView):

    def make_two_choices_task(self, task):

        questions = task.question_set.all()
        options = questions[0].option_set.all() if len(questions) else []

        self.sheet.merge_cells(f'F{self.row_cnt}:J{self.row_cnt}')
        self.sheet[f'F{self.row_cnt}'] = options[0].text
        self.sheet[f'F{self.row_cnt}'].alignment = Alignment(horizontal='center')

        self.sheet.merge_cells(f'K{self.row_cnt}:M{self.row_cnt}')
        self.sheet[f'K{self.row_cnt}'] = options[1].text
        self.sheet[f'K{self.row_cnt}'].alignment = Alignment(horizontal='center')
        self.row_cnt += 1

        self.sheet.row_dimensions[self.row_cnt].height = 10
        self.row_cnt += 1

        box_path = os.path.join(settings.STATIC_ROOT, 'box.jpeg')
        checked_box_path = os.path.join(settings.STATIC_ROOT, 'checked_box.jpeg')

        for question in questions:
            self.sheet.merge_cells(f'B{self.row_cnt}:E{self.row_cnt}')
            self.sheet[f'B{self.row_cnt}'] = question.text

            options = question.option_set.all()
            correct_option = options.filter(is_correct=True).first()

            if correct_option.text == options[0].text:
                box = self.prepare_image_for_cell(box_path, col=7)
                checked_box = self.prepare_image_for_cell(checked_box_path, col=11)
            else:
                box = self.prepare_image_for_cell(box_path, col=11)
                checked_box = self.prepare_image_for_cell(checked_box_path, col=7)

            self.sheet.add_image(box)
            self.sheet.add_image(checked_box)

            self.row_cnt += 1
            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1

    def make_choices_task(self, task):

        questions = task.question_set.all()

        for question in questions:
            self.sheet.merge_cells(f'B{self.row_cnt}:O{self.row_cnt}')
            self.sheet[f'B{self.row_cnt}'] = question.text
            self.row_cnt += 1

            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1

            char = ord('a')
            for option in question.option_set.all():

                self.sheet[f'C{self.row_cnt}'] = f'{chr(char)})'
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='center')
                char += 1

                self.sheet.merge_cells(f'D{self.row_cnt}:O{self.row_cnt}')
                self.sheet[f'D{self.row_cnt}'] = option.text

                if (option.is_correct):
                    self.sheet[f'C{self.row_cnt}'].font = Font(name='Calibri', bold=True)
                    self.sheet[f'D{self.row_cnt}'].font = Font(name='Calibri', bold=True)

                self.row_cnt += 1

                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1


    def make_choices_picture_task(self, task):

        question = task.question_set.first()

        self.sheet.merge_cells(f'C{self.row_cnt}:M{self.row_cnt + 5}')
        self.row_cnt += 7

        char = ord('a')
        for option in question.option_set.all():
            self.sheet.merge_cells(f'E{self.row_cnt}:M{self.row_cnt}')
            self.sheet[f'E{self.row_cnt}'] = f'{chr(char)}) {option.text}'

            if option.is_correct:
                self.sheet[f'E{self.row_cnt}'].font = Font(name='Calibri', bold=True)

            self.row_cnt += 1
            char += 1

            self.sheet.row_dimensions[self.row_cnt].height = 10
            self.row_cnt += 1


    def make_multiple_choices_picture_task(self, task):

        questions = task.question_set.all()

        self.sheet.merge_cells(f'C{self.row_cnt}:M{self.row_cnt + 5}')
        self.row_cnt += 7

        self.sheet.merge_cells(f'A{self.row_cnt}:O{self.row_cnt}')
        all_options = [option.text for option in questions[0].option_set.all()]
        self.sheet[f'A{self.row_cnt}'] = f'Výběr pojmů: {", ".join(all_options)}'
        self.row_cnt += 3

        for i in range(len(all_options)):

            question = questions.filter(text=i + 1).first()
            correct_answer = question.option_set.get(is_correct=True).text

            if i % 2 == 0:
                self.sheet[f'C{self.row_cnt}'] = f'{i + 1}.  '
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='right')

                self.sheet.merge_cells(f'D{self.row_cnt}:G{self.row_cnt}')
                self.sheet[f'D{self.row_cnt}'].border = Border(bottom=Side(style='thin'))
                self.sheet[f'D{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'D{self.row_cnt}'] = correct_answer

            else:
                self.sheet[f'I{self.row_cnt}'] = f'{i + 1}.  '
                self.sheet[f'I{self.row_cnt}'].alignment = Alignment(horizontal='right')

                self.sheet.merge_cells(f'J{self.row_cnt}:M{self.row_cnt}')
                self.sheet[f'J{self.row_cnt}'].border = Border(bottom=Side(style='thin'))
                self.sheet[f'J{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'J{self.row_cnt}'] = correct_answer

                self.row_cnt += 1


                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1

            self.row_cnt += 1


    def make_pairs_task(self, task):

            questions = task.question_set.all()
            options = list(questions[0].option_set.all() if len(questions) else [])

            for i, question in enumerate(questions):
                self.sheet.merge_cells(f'C{self.row_cnt}:F{self.row_cnt}')
                self.sheet[f'C{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'C{self.row_cnt}'] = question.text

                self.sheet.merge_cells(f'G{self.row_cnt}:I{self.row_cnt}')
                self.sheet[f'G{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'G{self.row_cnt}'] = '-'

                self.sheet.merge_cells(f'J{self.row_cnt}:M{self.row_cnt}')
                self.sheet[f'J{self.row_cnt}'].alignment = Alignment(horizontal='center')
                self.sheet[f'J{self.row_cnt}'] = options[i].text

                self.row_cnt += 1

                self.sheet.row_dimensions[self.row_cnt].height = 10
                self.row_cnt += 1