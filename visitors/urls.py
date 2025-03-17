from django.urls import path

from .exports import StatsExportView
from .views import VisitorCreateView, SchoolGroupsView, VisitorView, SubmitResultsView, VisitorUpdateView, \
    BetterThanView, StatsPageView, FetchStatsAjaxView

app_name = 'visitors'

urlpatterns = [
    path('stats/', StatsPageView.as_view(), name='stats'),
    path('stats/fetch/', FetchStatsAjaxView.as_view(), name='fetch_stats'),
    path('stats/export/', StatsExportView.as_view(), name='export_stats'),

    path("api/<int:visitor_id>/", VisitorView.as_view(), name='visitor'),
    path('api/create/', VisitorCreateView.as_view(), name='create'),
    path('api/<int:visitor_id>/update/', VisitorUpdateView.as_view(), name='update_visitor'),
    path('api/school-groups/', SchoolGroupsView.as_view(), name='school-groups'),
    path('api/<int:visitor_id>/submit-results/', SubmitResultsView.as_view(), name='submit-responses'),
    path('api/<int:visitor_id>/better-than/', BetterThanView.as_view(), name='better-than'),
]
