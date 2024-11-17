from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
from .views import CustomLoginView

urlpatterns = [
    path('', RedirectView.as_view(url='/areas/list', permanent=False)),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),

    path("areas/", include("areas.urls")),
    path("worksheets/", include("worksheets.urls")),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
