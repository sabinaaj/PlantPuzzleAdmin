from django.urls import path

from .views import WorksheetListView, WorksheetTemplateView
from . import views

app_name = "worksheets"

urlpatterns = [
    path("list", WorksheetListView.as_view(), name="worksheets_list"),
    path("create", WorksheetTemplateView.as_view(), name="worksheets_create"),
    path('load_task_form/<str:task_type>/', views.load_task_form, name='load_task_form'),
]

