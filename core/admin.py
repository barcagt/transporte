from django.contrib import admin
from .models import Bus, Pasajero, Ruta, Viaje, Boleto

admin.site.register(Bus)
admin.site.register(Pasajero)
admin.site.register(Ruta)
admin.site.register(Viaje)
admin.site.register(Boleto)