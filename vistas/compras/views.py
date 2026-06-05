"""
portal_compras.py — Vistas del módulo de compras de entradas.

Implementa el flujo de compra de tickets con integración a Mercado Pago:

FLUJO:
1. seleccion_asientos_view: Muestra la sala con los asientos disponibles/ocupados.
2. procesar_pago_view: Verifica asientos, guarda en sesión, crea preferencia MP,
   retorna la URL de pago para que el frontend abra en nueva pestaña.
3. verificar_pago_view: El usuario vuelve y hace clic en "Ya pagué".
   Busca el pago en la API de MP usando external_reference.
   Si aprobado → crea Venta + Tickets + QR.
4. ver_tickets_view: Muestra los tickets generados con sus QR.
"""

import json
import uuid
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from sistema_cine.models import Funcion, Asiento, Ticket

from servicios.compra_service import confirmar_compra
from servicios.mercadopago_service import ServicioMercadoPago


# ─── VISTA 1: SELECCIÓN DE ASIENTOS ──────────────────────────────────────────

@login_required
def seleccion_asientos_view(request, funcion_id):
    """
    Renderiza la sala y sus asientos para una función específica.
    """
    funcion = get_object_or_404(Funcion, id=funcion_id)
    sala = funcion.sala
    asientos = sala.asientos.filter(estado_asiento='activo')

    asientos_ocupados_ids = Ticket.objects.filter(
        funcion=funcion
    ).values_list('asiento_id', flat=True)

    layout = sala.layout_config if sala.layout_config else {}

    return render(request, 'portal/seleccion_asientos.html', {
        'funcion': funcion,
        'sala': sala,
        'layout': json.dumps(layout),
        'asientos_ocupados': list(asientos_ocupados_ids),
        'asientos_totales': asientos
    })


# ─── VISTA 2: PROCESAR PAGO (CREAR PREFERENCIA EN MP) ────────────────────────

@login_required
@require_POST
def procesar_pago_view(request, funcion_id):
    """
    Crea una preferencia de pago en Mercado Pago.
    Retorna la URL de pago para que el frontend abra en nueva pestaña.
    """
    funcion = get_object_or_404(Funcion, id=funcion_id)

    try:
        data = json.loads(request.body)
        asientos_ids = data.get('asientos_ids', [])

        if not asientos_ids:
            return JsonResponse({'error': 'No seleccionaste ningún asiento.'}, status=400)

        # Verificar que los asientos existen
        asientos = Asiento.objects.filter(id__in=asientos_ids)
        if asientos.count() != len(asientos_ids):
            return JsonResponse({'error': 'Algunos asientos no son válidos.'}, status=400)

        # ─── BARRERA 1: Verificar disponibilidad ──────────────────────────────
        asientos_ocupados = Ticket.objects.filter(
            funcion=funcion,
            asiento_id__in=asientos_ids
        ).values_list('asiento_id', flat=True)

        if asientos_ocupados:
            return JsonResponse({
                'error': 'Algunos asientos ya fueron comprados. Recargá la página.'
            }, status=409)

        monto_total = len(asientos_ids) * funcion.precio_entrada

        # Generar referencia única para vincular este pago con nuestra sesión
        referencia = f"cinefsa-{uuid.uuid4().hex[:12]}"

        # Guardar en sesión
        request.session['compra_pendiente'] = {
            'funcion_id': funcion_id,
            'asientos_ids': asientos_ids,
            'monto_total': str(monto_total),
            'referencia': referencia,
        }

        # Crear preferencia en Mercado Pago
        mp = ServicioMercadoPago()
        resultado = mp.crear_preferencia(
            funcion=funcion,
            cantidad_asientos=len(asientos_ids),
            monto_total=monto_total,
            external_reference=referencia,
            request=request,
        )

        return JsonResponse({
            'init_point': resultado['init_point'],
            'referencia': referencia,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─── VISTA 3: VERIFICAR PAGO (el usuario hace clic en "Ya pagué") ────────────

@login_required
def verificar_pago_view(request):
    """
    Busca en la API de Mercado Pago si existe un pago aprobado para
    la referencia guardada en la sesión.

    Se llama por AJAX cuando el usuario hace clic en "Ya pagué".
    """
    compra = request.session.get('compra_pendiente')
    if not compra:
        return JsonResponse({'status': 'error', 'mensaje': 'No hay compra en proceso.'}, status=400)

    referencia = compra.get('referencia')
    if not referencia:
        return JsonResponse({'status': 'error', 'mensaje': 'Referencia no encontrada.'}, status=400)

    # Buscar el pago en la API de MP usando la referencia
    mp = ServicioMercadoPago()
    pago = mp.buscar_pago_por_referencia(referencia)

    if not pago:
        return JsonResponse({
            'status': 'not_found',
            'mensaje': 'Todavía no detectamos tu pago. Si ya pagaste, esperá unos segundos e intentá de nuevo.',
        })

    if pago['status'] == 'approved':
        # ─── PAGO APROBADO: Crear Venta + Tickets + QR ───────────────────
        resultado = confirmar_compra(request, compra)
        return JsonResponse(resultado)

    elif pago['status'] in ('pending', 'in_process'):
        return JsonResponse({
            'status': 'pending',
            'mensaje': 'Tu pago está siendo procesado. Esperá unos momentos.',
        })

    else:
        # Rechazado u otro error
        if 'compra_pendiente' in request.session:
            del request.session['compra_pendiente']
        return JsonResponse({
            'status': 'rejected',
            'mensaje': f'Tu pago fue rechazado. Detalle: {pago.get("status_detail", "desconocido")}',
        })


# ─── VISTA 4: VER TICKETS ────────────────────────────────────────────────────

@login_required
def ver_tickets_view(request, venta_id):
    """Muestra los tickets generados de una venta con sus códigos QR."""
    from sistema_cine.models import Venta
    venta = get_object_or_404(Venta, id_venta=venta_id, usuario=request.user)
    tickets = venta.tickets.select_related('funcion__pelicula', 'asiento', 'funcion__sala')

    return render(request, 'portal/ver_tickets.html', {
        'venta': venta,
        'tickets': tickets,
        'titulo_pagina': f'Tickets - Venta #{venta.id_venta}',
    })
