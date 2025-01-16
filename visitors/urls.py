from django.urls import path

from .views import RegisterView, LoginView, UsernameCheckView, SchoolGroupsView, VisitorView, SubmitResponsesView, \
    SubmitSuccessRateView

app_name = 'visitors'

urlpatterns = [
    path("api/<int:visitor_id>/", VisitorView.as_view(), name='visitor'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/username-check/<str:username>/', UsernameCheckView.as_view(), name='username-check'),
    path('api/school-groups/', SchoolGroupsView.as_view(), name='school-groups'),
    path('api/submit-responses/', SubmitResponsesView.as_view(), name='submit-responses'),
    path('api/submit-success-rate/', SubmitSuccessRateView.as_view(), name='submit-success-rate'),
]