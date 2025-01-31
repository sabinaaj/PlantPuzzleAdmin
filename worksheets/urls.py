from django.urls import path

from .views import WorksheetListView, WorksheetCreateView, LoadTaskFormView, WorksheetDeleteView, \
    WorksheetUpdateView, CheckFormDataAjaxView, WorksheetsByAreaAPIView, WorksheetAPIView

from .exports import WorksheetExportView, WorksheetExportWithAnswersView

app_name = 'worksheets'

urlpatterns = [
    path('<int:area>/list', WorksheetListView.as_view(), name='worksheets_list'),
    path('<int:area>/create', WorksheetCreateView.as_view(), name='worksheets_create'),
    path('<int:area>/update/<int:pk>', WorksheetUpdateView.as_view(), name='worksheets_update'),
    path('<int:area>/delete/<int:pk>', WorksheetDeleteView.as_view(), name='worksheets_delete'),
    path('<int:area>/export/<int:pk>', WorksheetExportView.as_view(), name='worksheets_export'),
    path('<int:area>/export-with-answers/<int:pk>', WorksheetExportWithAnswersView.as_view(), name='worksheets_export_with_answers'),

    path('load-task-form/<str:task_type>/', LoadTaskFormView.as_view(), name='load_task_form'),
    path('check-form-data/', CheckFormDataAjaxView.as_view(), name='check_form_data'),

    path('api/<int:area_id>/<int:visitor_id>/worksheets/', WorksheetsByAreaAPIView.as_view(), name='worksheets_by_area'),
    path('api/<int:worksheet_id>/worksheet/', WorksheetAPIView.as_view(), name='worksheet'),
]

