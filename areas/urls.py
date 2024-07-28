from django.urls import path

from .views import AreaListView, AreaCreateView, AreaUpdateView, AreaDeleteView, PlantListView

app_name = "areas"

urlpatterns = [
    path('list/', AreaListView.as_view(), name='area_list'),
    path('create/', AreaCreateView.as_view(), name='area_create'),
    path('<int:pk>/update/', AreaUpdateView.as_view(), name='area_update'),
    path('<int:pk>/delete/', AreaDeleteView.as_view(), name='area_delete'),
    path("plants/list", PlantListView.as_view(), name="plants_list"),
]

