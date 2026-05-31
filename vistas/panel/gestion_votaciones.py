"""
gestion_votaciones.py — Vistas del panel de gestión de votaciones (RF-A04).

Implementa el Monitor de Votaciones para administradores:

    - monitor_votaciones_view: Dashboard con listado de todas las encuestas,
      sus estadísticas de participación y estado.
    - detalle_encuesta_view: Resultados detallados de una encuesta específica
      con porcentajes y película ganadora destacada.
    - crear_encuesta_view: Formulario para crear una nueva encuesta de votación.
    - toggle_encuesta_view: Activa o desactiva una encuesta manualmente (POST).
    - eliminar_encuesta_view: Elimina una encuesta y todos sus votos (POST).

Todas las vistas están protegidas con @solo_administrador.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from sistema_cine.models import Encuesta
from formularios.panel import FormularioEncuesta

# Reutilizar el decorador de seguridad definido en gestion_usuarios
from vistas.panel.gestion_usuarios import solo_administrador


# ══════════════════════════════════════════════════════════════════════════════
#  MONITOR DE VOTACIONES — Vista principal del dashboard
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
def monitor_votaciones_view(request):
    """
    Dashboard principal del módulo de votaciones (RF-A04).

    Muestra:
        - Todas las encuestas existentes (activas e históricas).
        - Contador de votos totales por encuesta.
        - Estado de cada encuesta (activa / período activo / cerrada).
        - Película provisional ganadora en cada encuesta.
    """
    # Obtener todas las encuestas con sus relaciones prefetched para evitar N+1
    encuestas = Encuesta.objects.prefetch_related('peliculas', 'votos').order_by('-fecha_inicio')

    # Preparar datos enriquecidos para cada encuesta
    encuestas_data = []
    for encuesta in encuestas:
        total_votos = encuesta.total_votos()
        resultados = encuesta.resultados()
        ganadora = resultados[0]['pelicula'] if resultados and resultados[0]['cantidad'] > 0 else None

        encuestas_data.append({
            'encuesta': encuesta,
            'total_votos': total_votos,
            'ganadora': ganadora,
            'en_periodo': encuesta.esta_en_periodo(),
            'disponible': encuesta.esta_disponible(),
        })

    return render(request, 'panel/monitor_votaciones.html', {
        'titulo_pagina': 'Monitor de Votaciones',
        'encuestas_data': encuestas_data,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  DETALLE DE ENCUESTA — Resultados completos
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
def detalle_encuesta_view(request, encuesta_id):
    """
    Vista de resultados detallados de una encuesta específica (RF-A04).

    Muestra:
        - Datos generales de la encuesta.
        - Resultados por película con barras de porcentaje.
        - Película ganadora destacada.
        - Participación total.
    """
    encuesta = get_object_or_404(
        Encuesta.objects.prefetch_related('peliculas', 'votos'),
        pk=encuesta_id
    )

    resultados = encuesta.resultados()
    total_votos = encuesta.total_votos()
    ganadora = resultados[0] if resultados and resultados[0]['cantidad'] > 0 else None

    return render(request, 'panel/detalle_votacion.html', {
        'titulo_pagina': f'Resultados: {encuesta.titulo}',
        'encuesta': encuesta,
        'resultados': resultados,
        'total_votos': total_votos,
        'ganadora': ganadora,
        'en_periodo': encuesta.esta_en_periodo(),
        'disponible': encuesta.esta_disponible(),
    })


# ══════════════════════════════════════════════════════════════════════════════
#  CREAR ENCUESTA
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
def crear_encuesta_view(request):
    """
    Vista para crear una nueva encuesta de votación.

    GET: Muestra el formulario vacío.
    POST: Valida y guarda la encuesta. Redirige al monitor con mensaje de éxito.
    """
    if request.method == 'POST':
        formulario = FormularioEncuesta(request.POST)
        if formulario.is_valid():
            encuesta = formulario.save()
            messages.success(
                request,
                f'La encuesta "{encuesta.titulo}" fue creada correctamente. '
                f'¡Ya está disponible para que los clientes voten!'
            )
            return redirect('panel:monitor_votaciones')
        else:
            messages.error(request, 'Corregí los errores del formulario antes de guardar.')
    else:
        formulario = FormularioEncuesta()

    return render(request, 'panel/formulario_encuesta.html', {
        'titulo_pagina': 'Nueva Encuesta de Votación',
        'formulario': formulario,
        'modo': 'crear',
    })


# ══════════════════════════════════════════════════════════════════════════════
#  TOGGLE DE ESTADO — Activar / Desactivar encuesta
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
@require_POST
def toggle_encuesta_view(request, encuesta_id):
    """
    Alterna el estado activo/inactivo de una encuesta.

    Si está activa, la desactiva (cierra la votación).
    Si está inactiva, la activa (abre la votación).
    Solo acepta método POST.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)

    if encuesta.esta_activa:
        encuesta.esta_activa = False
        msg = f'La encuesta "{encuesta.titulo}" fue desactivada. Los clientes ya no pueden votar.'
    else:
        encuesta.esta_activa = True
        msg = f'La encuesta "{encuesta.titulo}" fue activada correctamente.'

    encuesta.save()
    messages.success(request, msg)
    return redirect('panel:monitor_votaciones')


# ══════════════════════════════════════════════════════════════════════════════
#  ELIMINAR ENCUESTA
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
@require_POST
def eliminar_encuesta_view(request, encuesta_id):
    """
    Elimina una encuesta y todos sus votos asociados (CASCADE en BD).
    Solo acepta método POST para evitar eliminaciones accidentales via GET.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    titulo = encuesta.titulo
    total_votos = encuesta.total_votos()
    encuesta.delete()

    if total_votos > 0:
        messages.success(
            request,
            f'La encuesta "{titulo}" y sus {total_votos} voto(s) fueron eliminados.'
        )
    else:
        messages.success(request, f'La encuesta "{titulo}" fue eliminada correctamente.')

    return redirect('panel:monitor_votaciones')
