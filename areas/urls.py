from django.urls import path

from .views import AreaListView, WorksheetListView

app_name = "areas"

urlpatterns = [
    path("", AreaListView.as_view(), name="area_list"),
    path("list", AreaListView.as_view(), name="area_list"),
    path("worksheet/list", WorksheetListView.as_view(), name="worksheet_list"),
]

