from django import forms

from areas.models import Area, Plant

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['title', 'icon']

    def clean_title(self):
        title = self.cleaned_data.get('title')

        instance = self.instance
        if instance.pk:
            if Area.objects.exclude(pk=instance.pk).filter(title=title).exists():
                raise forms.ValidationError('Oblast s tímto názvem již existuje.')
        else:
            if Area.objects.filter(title=title).exists():
                raise forms.ValidationError('Oblast s tímto názvem již existuje.')

        if len(title) > 50:
            raise forms.ValidationError('Název může mít max. 50 znaků.')

        return title


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name']
