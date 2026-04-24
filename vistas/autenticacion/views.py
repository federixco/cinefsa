"""
views.py — Vistas de autenticación del sistema CineFSA.

Implementa el requerimiento RF-C01 (Autenticación): registro de nuevos
usuarios, inicio de sesión, cierre de sesión e historial de transacciones.

Flujo de registro:
    1. El visitante completa el formulario con sus datos personales.
    2. Se crea un registro en la tabla 'usuario' (supertipo).
    3. Se crea un registro en la tabla 'cliente' (subtipo) con fecha_nacimiento.
    4. El usuario queda logueado automáticamente y es redirigido al portal.

Flujo de login:
    1. El usuario ingresa email y contraseña.
    2. Django verifica las credenciales contra la tabla 'usuario'.
    3. Si son válidas, se crea una sesión y se redirige al portal.

Flujo de logout:
    1. Se destruye la sesión del usuario.
    2. Se redirige a la página de login.

Historial:
    Muestra las transacciones del usuario logueado (preparado para cuando
    se implementen los modelos Venta y Ticket en pasos posteriores).
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from formularios.autenticacion import FormularioRegistro, FormularioLogin
from sistema_cine.models import Cliente


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTRO DE NUEVOS USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

def registro_view(request):
    """
    Vista de registro de nuevos clientes (RF-C01).

    GET:  Muestra el formulario de registro vacío.
    POST: Valida los datos, crea el Usuario + Cliente y redirige.

    Proceso:
        1. Valida el formulario (email único, contraseñas coinciden, etc.).
        2. Crea el registro en la tabla 'usuario' (el formulario lo maneja).
        3. Crea el registro en la tabla 'cliente' con la FK y fecha_nacimiento.
        4. Inicia sesión automáticamente y redirige al portal.
    """
    # Si el usuario ya está logueado, redirigir al inicio.
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            # Paso 1: Crear el registro en tabla 'usuario' (supertipo).
            usuario = formulario.save()

            # Paso 2: Crear el registro en tabla 'cliente' (subtipo).
            Cliente.objects.create(
                usuario_id_usuario=usuario,
                fecha_nacimiento=formulario.cleaned_data['fecha_nacimiento'],
            )

            # Paso 3: Iniciar sesión automáticamente después del registro.
            login(request, usuario)
            messages.success(
                request,
                f'¡Bienvenido/a, {usuario.nombre_completo}! '
                f'Tu cuenta fue creada exitosamente.'
            )
            return redirect('/')
    else:
        formulario = FormularioRegistro()

    return render(request, 'autenticacion/registro.html', {
        'formulario': formulario,
        'titulo_pagina': 'Crear cuenta',
    })


# ══════════════════════════════════════════════════════════════════════════════
#  INICIO DE SESIÓN
# ══════════════════════════════════════════════════════════════════════════════

def login_view(request):
    """
    Vista de inicio de sesión (RF-C01).

    GET:  Muestra el formulario de login.
    POST: Autentica al usuario y crea la sesión.

    Django verifica las credenciales contra la tabla 'usuario' usando
    el campo email como USERNAME_FIELD (definido en el modelo Usuario).
    El parámetro ?next= permite redirigir al usuario a la página que
    intentaba acceder antes de ser enviado al login por @login_required.
    """
    # Si el usuario ya está logueado, redirigir al inicio.
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        formulario = FormularioLogin(request, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)

            # Redirigir a la página solicitada originalmente (si existe)
            # o al portal de inicio por defecto.
            siguiente = request.GET.get('next', '/')
            messages.success(request, f'¡Hola, {usuario.nombre_completo}!')
            return redirect(siguiente)
    else:
        formulario = FormularioLogin()

    return render(request, 'autenticacion/login.html', {
        'formulario': formulario,
        'titulo_pagina': 'Iniciar sesión',
    })


# ══════════════════════════════════════════════════════════════════════════════
#  CIERRE DE SESIÓN
# ══════════════════════════════════════════════════════════════════════════════

def logout_view(request):
    """
    Vista de cierre de sesión (RF-C01).

    Destruye la sesión del usuario y redirige a la página de login.
    Solo acepta peticiones POST para prevenir cierre de sesión accidental
    por links directos o crawlers.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Cerraste sesión correctamente.')
    return redirect('autenticacion:login')


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORIAL DE TRANSACCIONES
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def historial_view(request):
    """
    Vista del historial de transacciones del usuario (RF-C01).

    Muestra todas las compras realizadas por el usuario logueado.
    Requiere autenticación (@login_required redirige a LOGIN_URL si
    el usuario no está logueado).

    Nota: Los modelos Venta y Ticket aún no están implementados.
    La vista está preparada para incorporarlos cuando se desarrollen
    los módulos RF-C02 (Compra Online) y RF-C03 (Ticket Digital).
    """
    # TODO: Cuando se implementen los modelos Venta y Ticket,
    # reemplazar la lista vacía por:
    # ventas = Venta.objects.filter(
    #     usuario_id_usuario=request.user
    # ).order_by('-fecha_hora_transaccion')
    ventas = []

    return render(request, 'autenticacion/historial.html', {
        'ventas': ventas,
        'titulo_pagina': 'Mi historial',
    })
