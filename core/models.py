from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Bus(models.Model):
    placa = models.CharField(max_length=20, unique=True)
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return self.placa

class Pasajero(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dpi = models.CharField(max_length=20, unique=True)
    correo = models.EmailField()

    def __str__(self):
        return self.user.username

class Ruta(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.origen} - {self.destino}"

class Viaje(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()

    def clean(self):
        if Viaje.objects.filter(bus=self.bus, fecha_hora=self.fecha_hora).exclude(id=self.id).exists():
            raise ValidationError("Este bus ya tiene un viaje en esa fecha y hora.")

    def __str__(self):
        return f"{self.ruta} - {self.fecha_hora}"

class Boleto(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.PositiveIntegerField()

    class Meta:
        unique_together = ('viaje', 'asiento')

    def clean(self):
        # ✅ Proteger si no hay viaje asignado
        if not hasattr(self, 'viaje') or self.viaje is None:
            return

        # Validar asiento dentro de capacidad
        if self.asiento > self.viaje.bus.capacidad:
            raise ValidationError("Número de asiento excede capacidad del bus")

        # Validar conflicto horario para el pasajero
        if Boleto.objects.filter(
            pasajero=self.pasajero,
            viaje__fecha_hora=self.viaje.fecha_hora
        ).exclude(id=self.id).exists():
            raise ValidationError("Ya tienes un viaje con la misma fecha y hora.")

        # Validar cantidad de boletos
        boletos = Boleto.objects.filter(viaje=self.viaje).count()
        if boletos >= self.viaje.bus.capacidad:
            raise ValidationError("No hay más asientos disponibles")

    def __str__(self):
        return f"Asiento {self.asiento} - {self.viaje}"