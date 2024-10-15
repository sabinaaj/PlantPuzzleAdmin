from django.contrib import admin
from .models import TaskType, Worksheet, Task, Question, Option


admin.site.register(TaskType)
admin.site.register(Worksheet)
admin.site.register(Task)
admin.site.register(Question)
admin.site.register(Option)