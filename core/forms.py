from django import forms
from .models import Boleto, Bus, Ruta, Viaje

class BoletoPurchaseForm(forms.Form):
    cantidad = forms.IntegerField(
        label='¿Cuántos boletos deseas?',
        min_value=1,
        initial=1,
        help_text='Puedes elegir hasta el número de asientos disponibles.'
    )
    asiento = forms.ChoiceField(
        label='Selecciona asiento (solo para 1 boleto)',
        required=False
    )

    def __init__(self, *args, available_seats=None, **kwargs):
        super().__init__(*args, **kwargs)
        available_seats = available_seats or []
        choices = [('', 'Elige un asiento')] + [(str(seat), str(seat)) for seat in available_seats]
        self.fields['asiento'].choices = choices
        max_tickets = min(5, len(available_seats)) or 1
        self.fields['cantidad'].max_value = max_tickets
        self.fields['cantidad'].widget.attrs.update({'min': 1, 'max': max_tickets})
        self.available_seats = available_seats

    def clean(self):
        cleaned = super().clean()
        cantidad = cleaned.get('cantidad')
        asiento = cleaned.get('asiento')

        if cantidad == 1 and not asiento:
            self.add_error('asiento', 'Selecciona el asiento para este boleto.')

        if cantidad and cantidad > len(self.available_seats):
            self.add_error('cantidad', f'Solo hay {len(self.available_seats)} asientos disponibles.')

        return cleaned

    def clean_asiento(self):
        asiento = self.cleaned_data.get('asiento')
        if asiento in (None, ''):
            return None
        return int(asiento)

class BoletoEditForm(forms.ModelForm):
    asiento = forms.ChoiceField(label='Asiento disponible')

    class Meta:
        model = Boleto
        fields = ['asiento']

    def __init__(self, *args, available_seats=None, **kwargs):
        super().__init__(*args, **kwargs)
        available_seats = available_seats or []
        self.fields['asiento'].choices = [(str(seat), str(seat)) for seat in available_seats]

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