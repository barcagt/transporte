from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Viaje, Boleto, Pasajero, Bus, Ruta
from .forms import BoletoPurchaseForm, BoletoEditForm, BusForm, RutaForm, ViajeForm

def lista_viajes(request):
    viajes = Viaje.objects.all()
    return render(request, 'lista.html', {'viajes': viajes})

def registro(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        correo = request.POST['correo']
        dpi = request.POST['dpi']

        user = User.objects.create_user(
            username=username,
            password=password,
            email=correo
        )

        Pasajero.objects.create(
            user=user,
            dpi=dpi,
            correo=correo
        )

        login(request, user)
        return redirect('lista_viajes')

    return render(request, 'registro.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('lista_viajes')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def get_pasajero(request):
    pasajero, _ = Pasajero.objects.get_or_create(
        user=request.user,
        defaults={
            'dpi': '0000',
            'correo': request.user.email or 'correo@test.com'
        }
    )
    return pasajero


def build_seat_layout(capacidad, ocupados):
    ocupados = set(ocupados)
    return [
        {
            'numero': n,
            'status': 'ocupado' if n in ocupados else 'disponible'
        }
        for n in range(1, capacidad + 1)
    ]

@login_required
def comprar_boleto(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)

    pasajero = get_pasajero(request)

    ocupados = set(Boleto.objects.filter(viaje=viaje).values_list('asiento', flat=True))
    capacidad = viaje.bus.capacidad
    disponibles = [s for s in range(1, capacidad + 1) if s not in ocupados]
    seat_layout = build_seat_layout(capacidad, ocupados)

    if request.method == 'POST':
        form = BoletoPurchaseForm(request.POST, available_seats=disponibles)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            asiento = form.cleaned_data.get('asiento')

            if cantidad == 1:
                asientos = [int(asiento)]
            else:
                asientos = disponibles[:cantidad]

            try:
                for asiento_num in asientos:
                    boleto = Boleto(viaje=viaje, pasajero=pasajero, asiento=asiento_num)
                    boleto.full_clean()
                    boleto.save()
                return redirect('mis_boletos')
            except Exception as e:
                form.add_error(None, e)
    else:
        form = BoletoPurchaseForm(available_seats=disponibles)

    return render(request, 'comprar.html', {
        'form': form,
        'viaje': viaje,
        'ocupados': ocupados,
        'disponibles': disponibles,
        'capacidad': capacidad,
        'seat_layout': seat_layout
    })

@login_required
def admin_panel(request):
    if not request.user.is_staff:
        return redirect('lista_viajes')

    buses = Bus.objects.all()
    rutas = Ruta.objects.all()
    viajes = Viaje.objects.all().order_by('fecha_hora')
    mensaje = ''

    bus_form = BusForm(prefix='bus')
    ruta_form = RutaForm(prefix='ruta')
    viaje_form = ViajeForm(prefix='viaje')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'bus':
            bus_form = BusForm(request.POST, prefix='bus')
            if bus_form.is_valid():
                bus_form.save()
                mensaje = 'Bus creado correctamente.'
                bus_form = BusForm(prefix='bus')
        elif form_type == 'ruta':
            ruta_form = RutaForm(request.POST, prefix='ruta')
            if ruta_form.is_valid():
                ruta_form.save()
                mensaje = 'Ruta creada correctamente.'
                ruta_form = RutaForm(prefix='ruta')
        elif form_type == 'viaje':
            viaje_form = ViajeForm(request.POST, prefix='viaje')
            if viaje_form.is_valid():
                viaje_form.save()
                mensaje = 'Viaje creado correctamente.'
                viaje_form = ViajeForm(prefix='viaje')

    return render(request, 'admin_panel.html', {
        'buses': buses,
        'rutas': rutas,
        'viajes': viajes,
        'bus_form': bus_form,
        'ruta_form': ruta_form,
        'viaje_form': viaje_form,
        'mensaje': mensaje,
    })

@login_required
def mis_boletos(request):
    pasajero = get_pasajero(request)
    boletos = Boleto.objects.filter(pasajero=pasajero)
    return render(request, 'mis_boletos.html', {'boletos': boletos})

@login_required
def editar_boleto(request, boleto_id):
    boleto = get_object_or_404(Boleto, id=boleto_id, pasajero__user=request.user)
    viaje = boleto.viaje

    ocupados = list(Boleto.objects.filter(viaje=viaje).exclude(id=boleto.id).values_list('asiento', flat=True))
    disponibles = [s for s in range(1, viaje.bus.capacidad + 1) if s not in ocupados]
    available_seats = sorted(set(disponibles + [boleto.asiento]))

    if request.method == 'POST':
        form = BoletoEditForm(request.POST, instance=boleto, available_seats=available_seats)
        if form.is_valid():
            try:
                form.save()
                return redirect('mis_boletos')
            except Exception as e:
                form.add_error(None, e)
    else:
        form = BoletoEditForm(instance=boleto, available_seats=available_seats)

    return render(request, 'editar_boleto.html', {
        'form': form,
        'boleto': boleto,
        'viaje': viaje,
    })

@login_required
def eliminar_boleto(request, boleto_id):
    boleto = get_object_or_404(Boleto, id=boleto_id, pasajero__user=request.user)

    if request.method == 'POST':
        boleto.delete()
        return redirect('mis_boletos')

    return render(request, 'confirmar_eliminar_boleto.html', {'boleto': boleto})