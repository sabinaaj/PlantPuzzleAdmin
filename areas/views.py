from django.views.generic import TemplateView

class AreaListView(TemplateView):
    template_name = "areas_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context
