from django.urls import path

from .views import VisitorCreateView, SchoolGroupsView, VisitorView, SubmitResultsView, VisitorUpdateView, BetterThanView
app_name = 'visitors'

urlpatterns = [
    path("api/<int:visitor_id>/", VisitorView.as_view(), name='visitor'),
    path('api/create/', VisitorCreateView.as_view(), name='create'),
    path('api/<int:visitor_id>/update/', VisitorUpdateView.as_view(), name='update_visitor'),
    path('api/school-groups/', SchoolGroupsView.as_view(), name='school-groups'),
    path('api/<int:visitor_id>/submit-results/', SubmitResultsView.as_view(), name='submit-responses'),
    path('api/<int:visitor_id>/better-than/', BetterThanView.as_view(), name='better-than'),
]
