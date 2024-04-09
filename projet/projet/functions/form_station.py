from django import forms
from projet.models.stations import Station
from asgiref.sync import sync_to_async
import asyncio

class StationSearchForm(forms.Form):
    stations = forms.ModelMultipleChoiceField(
        queryset=Station.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class CoursEauSelectForm(forms.Form):
    cours_eau = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(CoursEauSelectForm, self).__init__(*args, **kwargs)
        self.fields['cours_eau'].choices = asyncio.run(self.get_cours_eau_choices())

    @sync_to_async
    def get_cours_eau_choices(self):
        return [('', 'Sélectionner un cours d eau')] + [(cours_eau, cours_eau) for cours_eau in Station.objects.order_by('libelle_cours_eau').values_list('libelle_cours_eau', flat=True).distinct()]

# class CoursEauSelectForm(forms.Form):
#     cours_eau = forms.ChoiceField(
#         label='Cours d eau',
#         choices=[('', 'Sélectionner un cours d eau')] + [(cours_eau, cours_eau) for cours_eau in Station.objects.order_by('libelle_cours_eau').values_list('libelle_cours_eau', flat=True).distinct()],
#     )
# forms.py
 
class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
