from django.contrib import admin
from .models import SchoolGroup, Visitor, VisitorResponse, SuccessRate

admin.site.register(SchoolGroup)
admin.site.register(Visitor)
admin.site.register(VisitorResponse)
admin.site.register(SuccessRate)
