from django.urls import path

from .views import AreaListView
app_name = "areas"

urlpatterns = [
    path("list", AreaListView.as_view(), name="area_list"),
]

