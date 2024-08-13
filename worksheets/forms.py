from django import forms

from visitors.models import SchoolGroup
from worksheets.models import Worksheet, Task, Question, Option


class WorksheetForm(forms.ModelForm):
    school_group = forms.ModelMultipleChoiceField(
        queryset=SchoolGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Určeno pro",
        required=False  # nebo False, pokud nemá být povinné
    )

    class Meta:
        model = Worksheet
        fields = ["title", "school_group"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['text', 'type']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image']


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
