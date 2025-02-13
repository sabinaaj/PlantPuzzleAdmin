from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AreaListView, AreaCreateView, AreaUpdateView, AreaDeleteView, PlantListView, AreaViewSet, \
    PlantCreateView, PlantUpdateView, PlantDeleteView, CheckFormDataAjaxView, GetAreaStats

app_name = 'areas'

router = DefaultRouter()
router.register(r'areas', AreaViewSet)

urlpatterns = [
    path('list/', AreaListView.as_view(), name='area_list'),
    path('create/', AreaCreateView.as_view(), name='area_create'),
    path('<int:pk>/update/', AreaUpdateView.as_view(), name='area_update'),
    path('<int:pk>/delete/', AreaDeleteView.as_view(), name='area_delete'),

    path('<int:area>/plants/list', PlantListView.as_view(), name='plants_list'),
    path('<int:area>/plants/create', PlantCreateView.as_view(), name='plants_create'),
    path('<int:area>/plants/<int:pk>/update', PlantUpdateView.as_view(), name='plants_update'),
    path('<int:area>/plants/<int:pk>/delete', PlantDeleteView.as_view(), name='plants_delete'),

    path('check-form-data/', CheckFormDataAjaxView.as_view(), name='check_form_data'),

    path('api/', include(router.urls)),
    path('api/<int:area_id>/<int:visitor_id>/get-area-stats/', GetAreaStats.as_view(), name='get_area_stats'),
]
