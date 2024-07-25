from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import Worksheet



class WorksheetListView(TemplateView):
    template_name = "worksheets_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context


class WorksheetTemplateView(TemplateView):
    template_name = "worksheets_create.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context


def load_task_form(request, task_type):
    if task_type == "1":
        template_name = 'task_type_1.html'
    elif task_type == "2":
        template_name = 'task_type_2.html'
    elif task_type == "3":
        template_name = 'task_type_3.html'
    elif task_type == "4":
        template_name = 'task_type_4.html'
    elif task_type == "5":
        template_name = 'task_type_5.html'
    else:
        return JsonResponse({'error': 'Invalid task type'}, status=400)

    html_content = render_to_string(template_name, request=request)
    return JsonResponse({'html': html_content})
