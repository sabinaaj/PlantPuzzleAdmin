from django import forms

from visitors.models import SchoolGroup
from worksheets.models import Worksheet, Task, Question, Option


class WorksheetForm(forms.ModelForm):
    school_group = forms.ModelMultipleChoiceField(
        queryset=SchoolGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Určeno pro",
        required=False
    )

    class Meta:
        model = Worksheet
        fields = ["title", "school_group"]
