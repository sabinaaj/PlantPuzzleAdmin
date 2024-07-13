from django.views.generic import TemplateView

from .models import Worksheet


class WorksheetListView(TemplateView):
    template_name = "worksheets_create.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context
