from django.contrib.auth.views import LoginView
from django.urls import reverse

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse('areas:area_list')