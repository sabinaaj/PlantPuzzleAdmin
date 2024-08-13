from django.urls import path

from .views import WorksheetListView, WorksheetCreateView, LoadTaskFormView

app_name = "worksheets"

urlpatterns = [
    path("<int:area>/list", WorksheetListView.as_view(), name="worksheets_list"),
    path("<int:area>/create", WorksheetCreateView.as_view(), name="worksheets_create"),
    path('<int:area>/load_task_form/<str:task_type>/', LoadTaskFormView.as_view(), name='load_task_form'),
]

