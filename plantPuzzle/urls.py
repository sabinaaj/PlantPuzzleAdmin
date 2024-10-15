from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/areas/list', permanent=False)),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),

    path("areas/", include("areas.urls")),

    path("worksheets/", include("worksheets.urls"))

]