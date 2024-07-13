from django.urls import path

from .views import WorksheetListView

app_name = "worksheets"

urlpatterns = [
    path("list", WorksheetListView.as_view(), name="worksheets_list"),
]

