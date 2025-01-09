from django.urls import path

from .views import RegisterView

app_name = "visitors"

urlpatterns = [
    # path('api/login/', obtain_jwt_token),
    # path('api/token-refresh/', refresh_jwt_token),
    path('api/register/', RegisterView.as_view(), name='register'),
]