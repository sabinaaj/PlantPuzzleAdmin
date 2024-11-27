from django.views.generic import View
from django.shortcuts import get_object_or_404
from random import shuffle

from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Worksheet

import pdfkit
import re

from .views import logger

class WorksheetExportView(View):

    def get(self, request, *args, **kwargs):

        self.worksheet = get_object_or_404(Worksheet, pk=kwargs['pk'])

        context = {

            'worksheet_title': self.worksheet.title,
            'tasks': [
                {
                    'type': task.type.id,
                    'text': f'{i + 1}. {task.text}' or '',
                    'image': task.taskimage_set.first().image.path if task.taskimage_set.exists() else '',
                    'questions': self.prepare_task_data(task),
                }
                for i, task in enumerate(self.worksheet.task_set.all())
            ]
        }

        options = {'enable-local-file-access': ''}

        html_content = render_to_string('worksheet_export.html', context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=pracovni_list.pdf'

        pdf = pdfkit.from_string(html_content, False, options=options)
        response.write(pdf)

        return response

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

        logger.warning(any(len(question.text) > 50 for question in questions))

        return {
            'align_left': True if any(len(question.text) > 50 for question in questions) else False,
            'options': [option.text if option.text else "" for option in options],
            'questions': [question.text for question in questions]
        }

    def prepare_type_2_or_3_task_data(self, task):
        question = task.question_set.first()
        options = question.option_set.all() if question else []
        char = ord('a')

        return {
            'question': question.text if question.text else '',
            'options': [f'{chr(char+i)}) {option.text}' for i, option in enumerate(options)],
        }

    def prepare_type_4_task_data(self, task):
        options = task.question_set.first().option_set.all()
        options = [option.text if option.text else "" for option in options]


        return {
            'count': range(1, task.question_set.count() + 1),
            'options': ", ".join(options),
        }

    def prepare_type_5_task_data(self, task):
        questions = task.question_set.all()
        options = list(questions[0].option_set.all().values('text') if questions[0] else [])
        shuffle(options)

        return {
            'questions': [
                {
                    'text': question.text if question.text else '',
                    'option': options[i]['text'],
                }
                for i, question in enumerate(questions)
            ],
        }


class WorksheetExportWithAnswersView(View):

    def get(self, request, *args, **kwargs):

        self.worksheet = get_object_or_404(Worksheet, pk=kwargs['pk'])

        context = {

            'worksheet_title': self.worksheet.title,
            'tasks': [
                {
                    'type': task.type.id,
                    'text': f'{i + 1}. {task.text}' or '',
                    'image': task.taskimage_set.first().image.path if task.taskimage_set.exists() else '',
                    'questions': self.prepare_task_data(task),
                }
                for i, task in enumerate(self.worksheet.task_set.all())
            ]
        }

        options = {'enable-local-file-access': ''}

        html_content = render_to_string('worksheet_export_with_answers.html', context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=pracovni_list_s_odpovedmi.pdf'

        pdf = pdfkit.from_string(html_content, False, options=options)
        response.write(pdf)

        return response

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
            'align_left': True if any(len(question.text) > 50 for question in questions) else False,
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
        char = ord('a')

        return {
            'question': question.text if question.text else '',
            'options': [
                {'text': f'{chr(char+i)}) {option.text}' if option.text else '',
                 'correct': True if option.is_correct else False}
                for i, option in enumerate(options)
            ],
        }

    def prepare_type_4_task_data(self, task):
        questions = task.question_set.all()
        options = questions[0].option_set.all() if questions[0] else []
        options = [option.text if option.text else "" for option in options]

        correct_answers = []

        for i in range(len(questions)):

            question = questions.filter(text=i + 1).first()
            correct_answer = question.option_set.get(is_correct=True).text if question.option_set.get(is_correct=True) else ''

            correct_answers.append({
                'text': i + 1,
                'correct': correct_answer
            })

        return {
            'options': ", ".join(options),
            'correct_answers': correct_answers
        }


    def prepare_type_5_task_data(self, task):
        questions = task.question_set.all()

        return {
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
