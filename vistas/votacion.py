"""
votacion.py — Vistas del módulo de Cine Club / Votación (RF-C04).

Implementa:
    - votacion_view: Muestra la encuesta activa con las películas candidatas.
      Si el usuario no está autenticado, muestra un banner invitándolo a
      registrarse. Si ya votó, muestra su elección y los resultados parciales.
    - emitir_voto_view: Endpoint POST que registra el voto del cliente.
      Solo accesible para usuarios autenticados con perfil de Cliente.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from sistema_cine.models import Encuesta, Voto, Cliente


def votacion_view(request):
    """
    Vista pública del portal de Cine Club (RF-C04).

    Comportamiento según el estado del usuario:

    1. VISITANTE (no autenticado):
       - Ve las películas candidatas de la encuesta activa.
       - Ve un banner/cartelito que le indica que debe registrarse para votar.
       - No puede emitir votos.

    2. CLIENTE AUTENTICADO que NO votó todavía:
       - Ve las películas con botón de voto habilitado.

    3. CLIENTE AUTENTICADO que YA votó:
       - Ve su elección y los resultados parciales con barras de progreso.

    4. Sin encuesta activa:
       - Se muestra un mensaje informativo.
    """

    # Buscar la encuesta activa más reciente (activa manualmente y dentro del período)
    ahora = timezone.now()
    encuesta = Encuesta.objects.filter(
        esta_activa=True,
        fecha_inicio__lte=ahora,
        fecha_fin__gte=ahora
    ).prefetch_related('peliculas').first()

    # Estado del usuario respecto a la votación
    ya_voto = False
    voto_del_usuario = None
    resultados = []
    cliente = None

    if encuesta:
        # Calcular resultados para mostrar siempre (o solo si ya votó)
        resultados = encuesta.resultados()

        # Verificar si el usuario autenticado ya votó en esta encuesta
        if request.user.is_authenticated:
            try:
                cliente = request.user.cliente.first()
                if cliente:
                    voto_del_usuario = Voto.objects.filter(
                        cliente=cliente,
                        encuesta=encuesta
                    ).first()
                    ya_voto = voto_del_usuario is not None
            except Exception:
                pass

    return render(request, 'portal/cine_club.html', {
        'titulo_pagina': 'Cine Club — Votación',
        'encuesta': encuesta,
        'resultados': resultados,
        'ya_voto': ya_voto,
        'voto_del_usuario': voto_del_usuario,
        'cliente': cliente,
    })


@login_required(login_url='autenticacion:login')
@require_POST
def emitir_voto_view(request, encuesta_id):
    """
    Endpoint POST para registrar el voto de un cliente (RF-C04).

    Validaciones:
        1. El usuario autenticado debe tener perfil de Cliente.
        2. La encuesta debe existir, estar activa y dentro del período.
        3. La película votada debe ser candidata en esa encuesta.
        4. El cliente no debe haber votado antes en esta encuesta.

    En caso de éxito, redirige a la página de votación con mensaje de confirmación.
    En caso de error (ya votó, encuesta cerrada, etc.), redirige con mensaje de error.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)

    # ── Validación 1: Verificar que el usuario tiene perfil de Cliente ──────────
    cliente = request.user.cliente.first()
    if not cliente:
        messages.error(
            request,
            'Solo los clientes registrados pueden votar. '
            'Contactá al administrador si tu cuenta no tiene el rol de cliente.'
        )
        return redirect('cine_club')

    # ── Validación 2: La encuesta debe estar disponible ────────────────────────
    if not encuesta.esta_disponible():
        messages.error(request, 'La votación ya cerró o no está disponible.')
        return redirect('cine_club')

    # ── Validación 3: La película elegida debe ser candidata de esta encuesta ──
    pelicula_id = request.POST.get('pelicula_id')
    if not pelicula_id:
        messages.error(request, 'Debés seleccionar una película para votar.')
        return redirect('cine_club')

    pelicula = encuesta.peliculas.filter(pk=pelicula_id).first()
    if not pelicula:
        messages.error(request, 'La película seleccionada no es candidata en esta encuesta.')
        return redirect('cine_club')

    # ── Validación 4: Evitar voto duplicado (también controlado en la BD) ──────
    if Voto.objects.filter(cliente=cliente, encuesta=encuesta).exists():
        messages.warning(request, 'Ya emitiste tu voto en esta encuesta.')
        return redirect('cine_club')

    # ── Registrar el voto ──────────────────────────────────────────────────────
    Voto.objects.create(
        cliente=cliente,
        encuesta=encuesta,
        pelicula=pelicula
    )

    messages.success(
        request,
        f'¡Tu voto por "{pelicula.titulo}" fue registrado con éxito! '
        f'Gracias por participar en el Cine Club.'
    )
    return redirect('cine_club')
