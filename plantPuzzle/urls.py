from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import CustomLoginView

schema_view = get_schema_view(
    openapi.Info(
        title='API Dokumentace',
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='login', permanent=False)),
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),

    path('areas/', include('areas.urls')),
    path('worksheets/', include('worksheets.urls')),
    path('visitors/', include('visitors.urls')),


    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema_swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema_redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
