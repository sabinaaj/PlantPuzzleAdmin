from django.urls import path

from .views import VisitorCreateView, SchoolGroupsView, VisitorView, SubmitResponsesView, VisitorUpdateView,\
    SubmitSuccessRateView

app_name = 'visitors'

urlpatterns = [
    path("api/<int:visitor_id>/", VisitorView.as_view(), name='visitor'),
    path('api/create/', VisitorCreateView.as_view(), name='create'),
    path('api/<int:visitor_id>/update/', VisitorUpdateView.as_view(), name='update_visitor'),
    path('api/school-groups/', SchoolGroupsView.as_view(), name='school-groups'),
    path('api/submit-responses/', SubmitResponsesView.as_view(), name='submit-responses'),
    path('api/submit-success-rate/', SubmitSuccessRateView.as_view(), name='submit-success-rate'),
]