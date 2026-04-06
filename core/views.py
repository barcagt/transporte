from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Viaje, Boleto, Pasajero
from .forms import BoletoForm

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

@login_required
def comprar_boleto(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)

    pasajero, _ = Pasajero.objects.get_or_create(
        user=request.user,
        defaults={
            'dpi': '0000',
            'correo': request.user.email or 'correo@test.com'
        }
    )

    if request.method == 'POST':
        form = BoletoForm(request.POST)
        if form.is_valid():
            boleto = form.save(commit=False)
            boleto.viaje = viaje
            boleto.pasajero = pasajero

            try:
                boleto.full_clean()  # Valida con viaje asignado
                boleto.save()
                return redirect('mis_boletos')
            except Exception as e:
                form.add_error(None, e)
    else:
        form = BoletoForm()

    return render(request, 'comprar.html', {
        'form': form,
        'viaje': viaje
    })

@login_required
def mis_boletos(request):
    pasajero, _ = Pasajero.objects.get_or_create(
        user=request.user,
        defaults={'dpi': '0000', 'correo': request.user.email or 'correo@test.com'}
    )

    boletos = Boleto.objects.filter(pasajero=pasajero)
    return render(request, 'mis_boletos.html', {'boletos': boletos})