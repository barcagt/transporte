from django import forms
from .models import Boleto

class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = ['asiento']

    def clean(self):
        # Evita validación prematura
        return self.cleaned_data