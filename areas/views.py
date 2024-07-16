from django.views.generic import TemplateView

class AreaListView(TemplateView):
    template_name = "areas_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context

class AreaCreateView(TemplateView):
    template_name = "areas_create.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context

class AreaUpdateView(TemplateView):
    template_name = "areas_update.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        return context


class AreaDeleteView:
    pass

class PlantListView(TemplateView):
    template_name = "plants_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context