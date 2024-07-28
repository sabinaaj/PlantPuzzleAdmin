from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from areas.forms import AreaForm
from areas.models import Area


class AreaListView(ListView):
    model = Area
    template_name = "areas_list.html"
    context_object_name = "areas"


class AreaCreateView(CreateView):
    template_name = "areas_form.html"
    form_class = AreaForm
    model = Area

    def get_success_url(self):
        return reverse("areas:area_list")


class AreaUpdateView(UpdateView):
    template_name = "areas_form.html"
    form_class = AreaForm
    model = Area

    def get_success_url(self):
        return reverse("areas:area_list")

class AreaDeleteView(DeleteView):
    model = Area
    success_url = reverse_lazy("areas:area_list")

class PlantListView(TemplateView):
    template_name = "plants_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context