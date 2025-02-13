from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Avg
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from visitors.models import Visitor, SuccessRate
from worksheets.models import Worksheet
from worksheets.views import logger
from .serializers import AreaSerializer
from areas.forms import AreaForm, PlantForm
from areas.models import Area, Plant, PlantImage

import logging
logger = logging.getLogger(__name__)


class AreaListView(LoginRequiredMixin, ListView):
    model = Area
    template_name = 'areas_list.html'
    context_object_name = 'areas'


class AreaCreateView(LoginRequiredMixin, CreateView):
    template_name = 'areas_form.html'
    form_class = AreaForm
    model = Area

    def get_success_url(self):
        return reverse('areas:area_list')


class AreaUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'areas_form.html'
    form_class = AreaForm
    model = Area

    def get_success_url(self):
        return reverse('areas:area_list')


class AreaDeleteView(LoginRequiredMixin, DeleteView):
    model = Area
    success_url = reverse_lazy('areas:area_list')


class PlantListView(LoginRequiredMixin, TemplateView):
    template_name = 'plants_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['area'] = self.area
        context['plants'] = self.area.plant_set.all()

        return context


class PlantCreateView(LoginRequiredMixin, CreateView):
    template_name = 'plants_form.html'
    form_class = PlantForm
    model = Plant

    def get_success_url(self):
        return reverse('areas:plants_list',  kwargs={'area': self.area.pk})

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['area'] = self.area

        return context

    def form_valid(self, form):
        form.instance.area = self.area
        self.object = form.save()

        # Process images
        images = self.request.FILES
        for image in images.values():
            PlantImage.objects.create(
                plant=self.object,
                image=image
            )

        return super().form_valid(form)


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'plants_form.html'
    form_class = PlantForm
    model = Plant

    def get_success_url(self):
        return reverse('areas:plants_list',  kwargs={'area': self.area.pk})

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['area'] = self.area
        context['images'] = [{
            'pk': image.pk,
            'url': image.image.url}
            for image in PlantImage.objects.filter(plant=self.object)
        ]

        return context

    def form_valid(self, form):
        self.object = form.save()

        plant_images = []
        images = {k: v for (k, v) in self.request.POST.items() if k.endswith('image-original')}

        for key, image_pk in images.items():
            image_id = key.split('-')[0]

            if self.request.FILES.get(f'{image_id}-image'):
                image = PlantImage.objects.create(
                    plant=self.object,
                    image=self.request.FILES.get(f'{image_id}-image')
                )
                plant_images.append(image.pk)

            elif image_pk:
                plant_images.append(image_pk)

        # Delete old images
        PlantImage.objects.filter(plant=self.object).exclude(id__in=plant_images).delete()

        return super().form_valid(form)


class PlantDeleteView(LoginRequiredMixin, DeleteView):
    model = Plant

    def dispatch(self, request, *args, **kwargs):
        self.area = get_object_or_404(Area, pk=kwargs['area'])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('areas:plants_list',  kwargs={'area': self.area.pk})


class CheckFormDataAjaxView(View):

    errors = {}

    def post(self, request, *args, **kwargs):
        self.errors = {}
        logger.warning('CheckFormDataAjaxView: %s', request.POST)
        title = request.POST.get('name')

        if not title:
            self.errors['name'] = 'Název je povinný.'
        else:
            if len(title) > 100:
                self.errors['name'] = 'Název může mít max. 50 znaků.'

        if self.errors:
            return JsonResponse({'status': False, 'errors': self.errors})

        return JsonResponse({'status': True})



class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class GetAreaStats(APIView):

    def get(self, request, area_id, visitor_id):

        try:
            area = Area.objects.get(id=area_id)
            visitor = Visitor.objects.get(id=visitor_id)
        except Area.DoesNotExist:
            return Response(
                {"error": f"Area with id {area_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Visitor.DoesNotExist:
            return Response(
                {"error": f"Visitor with id {visitor_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        worksheets = Worksheet.objects.filter(area=area)
        # Get latest success rate for each worksheet and visitor combination
        latest_rates = (SuccessRate.objects.filter(worksheet__in=worksheets, visitor=visitor)
                        .order_by('worksheet', 'visitor', '-created_at')
                        .distinct('worksheet', 'visitor'))

        worksheet_cnt = worksheets.count()
        done_worksheets_cnt = latest_rates.count()

        # Count average success rate
        rates_list = list(latest_rates.values_list('rate', flat=True))
        avg_success_rate = sum(rates_list) / len(rates_list) if rates_list else 0

        return Response(
            {
                "worksheet_count": worksheet_cnt,
                "done_worksheet_count": done_worksheets_cnt,
                "average_success_rate": avg_success_rate,
            },
            status=status.HTTP_200_OK,
        )
