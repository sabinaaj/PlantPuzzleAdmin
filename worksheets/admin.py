from django.contrib import admin
from .models import TaskType, Worksheet, Task, Question, Option, TaskImage

admin.site.register(TaskType)
admin.site.register(Worksheet)
admin.site.register(Task)
admin.site.register(TaskImage)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'is_correct', 'question')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'task')
