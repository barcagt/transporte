from django import forms
from .models import Boleto, Bus, Ruta, Viaje

class BoletoForm(forms.ModelForm):
    asiento = forms.ChoiceField(label='Asiento')

    class Meta:
        model = Boleto
        fields = ['asiento']

    def __init__(self, *args, available_seats=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        if available_seats is not None:
            choices = [(str(seat), str(seat)) for seat in available_seats]
        self.fields['asiento'].choices = choices

    def clean_asiento(self):
        asiento = self.cleaned_data.get('asiento')
        return int(asiento)

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['placa', 'capacidad']

class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ['origen', 'destino', 'precio']

class ViajeForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Viaje
        fields = ['bus', 'ruta', 'fecha_hora']