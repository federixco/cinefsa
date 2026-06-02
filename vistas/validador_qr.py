"""
validador_qr.py — Vistas del módulo de validación de tickets por QR.

Permite a los empleados escanear códigos QR de tickets desde un dispositivo
con cámara (celular/tablet) y validar el ingreso de los clientes.

Reglas de validación:
- Solo se validan tickets cuya función sea del día actual.
- Ventana de escaneo: 30 min antes del inicio hasta 15 min después.
- Re-escaneo: muestra info al empleado, quien decide si permite re-ingreso.
"""

import json
from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from sistema_cine.models import Ticket
from .decoradores import solo_empleado


# ─── CONSTANTES DE VENTANA DE TIEMPO ─────────────────────────────────────────
MINUTOS_ANTES_APERTURA = 30   # Puertas abren 30 min antes de la función
MINUTOS_TOLERANCIA_DESPUES = 15  # Tolerancia de 15 min después del inicio


@login_required
@solo_empleado
def scanner_view(request):
    """
    Vista GET: Renderiza la página del escáner QR con acceso a la cámara.
    Solo accesible para usuarios con rol Empleado.
    """
    return render(request, 'panel/scanner_qr.html', {
        'titulo_pagina': 'Validador de Tickets',
    })


@login_required
@solo_empleado
@require_POST
def validar_ticket_api(request):
    """
    Vista POST (API JSON): Procesa la validación de un ticket escaneado.
    
    Recibe: { "codigo_qr": "uuid-del-ticket" }
    Responde JSON con status: 'success', 'warning' o 'error'.
    """
    try:
        data = json.loads(request.body)
        codigo_raw = data.get('codigo_qr', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Datos inválidos.',
        }, status=400)
    
    # Extraer UUID del formato "CINEFSA-TICKET-{uuid}"
    if codigo_raw.startswith('CINEFSA-TICKET-'):
        codigo = codigo_raw.replace('CINEFSA-TICKET-', '')
    else:
        codigo = codigo_raw
    
    if not codigo:
        return JsonResponse({
            'status': 'error',
            'mensaje': 'No se recibió código QR.',
        }, status=400)
    
    # ─── BUSCAR TICKET ────────────────────────────────────────────────────
    try:
        ticket = Ticket.objects.select_related(
            'funcion__pelicula', 'funcion__sala', 'asiento', 'venta'
        ).get(codigo_qr=codigo)
    except Ticket.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Ticket no encontrado. El código QR es inválido.',
            'icono': 'fa-times-circle',
        })
    
    # ─── DATOS DEL TICKET (para todas las respuestas) ─────────────────────
    datos_ticket = {
        'pelicula': ticket.funcion.pelicula.titulo,
        'sala': ticket.funcion.sala.nombre_sala,
        'asiento': f'{ticket.asiento.fila}{ticket.asiento.numero}',
        'fecha_funcion': ticket.funcion.fecha.strftime('%d/%m/%Y'),
        'hora_funcion': ticket.funcion.hora_inicio.strftime('%H:%M'),
        'tipo_asiento': ticket.asiento.get_tipo_asiento_display(),
    }
    
    # ─── VALIDAR ESTADO DE PAGO ───────────────────────────────────────────
    if ticket.venta.estado_pago != 'aprobado':
        return JsonResponse({
            'status': 'error',
            'mensaje': f'El pago de esta venta no está confirmado (Estado: {ticket.venta.get_estado_pago_display()}).',
            'icono': 'fa-credit-card',
            'ticket': datos_ticket,
        })
    
    # ─── VERIFICAR SI YA FUE VALIDADO ─────────────────────────────────────
    if ticket.estado_uso == 'validado':
        hora_val = timezone.localtime(ticket.fecha_validacion).strftime('%H:%M') if ticket.fecha_validacion else '—'
        return JsonResponse({
            'status': 'warning',
            'mensaje': f'Este ticket ya fue validado a las {hora_val}hs.',
            'icono': 'fa-exclamation-triangle',
            'ticket': datos_ticket,
        })
    
    # ─── VERIFICAR FECHA (debe ser hoy) ───────────────────────────────────
    ahora = timezone.now()
    hoy = timezone.localdate()
    
    if ticket.funcion.fecha != hoy:
        if ticket.funcion.fecha < hoy:
            return JsonResponse({
                'status': 'error',
                'mensaje': f'Esta función ya pasó ({datos_ticket["fecha_funcion"]}).',
                'icono': 'fa-calendar-times',
                'ticket': datos_ticket,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'mensaje': f'Esta función es para el {datos_ticket["fecha_funcion"]}, no es hoy.',
                'icono': 'fa-calendar-alt',
                'ticket': datos_ticket,
            })
    
    # ─── VERIFICAR VENTANA DE TIEMPO ──────────────────────────────────────
    from datetime import datetime
    
    hora_funcion = datetime.combine(hoy, ticket.funcion.hora_inicio)
    hora_funcion = timezone.make_aware(hora_funcion)
    
    hora_apertura = hora_funcion - timedelta(minutes=MINUTOS_ANTES_APERTURA)
    hora_limite = hora_funcion + timedelta(minutes=MINUTOS_TOLERANCIA_DESPUES)
    
    if ahora < hora_apertura:
        return JsonResponse({
            'status': 'error',
            'mensaje': f'Aún no es hora. Las puertas abren a las {hora_apertura.strftime("%H:%M")}hs.',
            'icono': 'fa-clock',
            'ticket': datos_ticket,
        })
    
    # Después de la tolerancia: warning pero PERMITE validar
    es_tarde = ahora > hora_limite
    
    # ─── VALIDAR TICKET ───────────────────────────────────────────────────
    ticket.estado_uso = 'validado'
    ticket.fecha_validacion = ahora
    ticket.save(update_fields=['estado_uso', 'fecha_validacion'])
    
    if es_tarde:
        minutos_tarde = int((ahora - hora_funcion).total_seconds() // 60)
        return JsonResponse({
            'status': 'warning',
            'mensaje': f'Validado ✓ — La función comenzó hace {minutos_tarde} min.',
            'icono': 'fa-exclamation-triangle',
            'ticket': datos_ticket,
            'validado': True,
        })
    
    return JsonResponse({
        'status': 'success',
        'mensaje': '¡Ticket validado correctamente!',
        'icono': 'fa-check-circle',
        'ticket': datos_ticket,
        'validado': True,
    })
