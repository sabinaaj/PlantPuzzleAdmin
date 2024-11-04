from django.urls import path

from .views import WorksheetListView, WorksheetCreateView, LoadTaskFormView, WorksheetDeleteView, WorksheetExportView, \
                   WorksheetExportWithAnswersView, WorksheetUpdateView

app_name = "worksheets"

urlpatterns = [
    path("<int:area>/list", WorksheetListView.as_view(), name="worksheets_list"),
    path("<int:area>/create", WorksheetCreateView.as_view(), name="worksheets_create"),
    path("<int:area>/update/<int:pk>", WorksheetUpdateView.as_view(), name="worksheets_update"),
    path("<int:area>/delete/<int:pk>", WorksheetDeleteView.as_view(), name="worksheets_delete"),
    path("<int:area>/export/<int:pk>", WorksheetExportView.as_view(), name="worksheets_export"),
    path("<int:area>/export_with_answers/<int:pk>", WorksheetExportWithAnswersView.as_view(), name="worksheets_export_with_answers"),

    path('load_task_form/<str:task_type>/', LoadTaskFormView.as_view(), name='load_task_form'),
]

