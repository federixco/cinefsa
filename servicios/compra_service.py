"""
compra_service.py — Servicio de confirmación de compras.

Contiene la lógica de negocio transaccional para confirmar una compra
una vez que el pago fue aprobado por Mercado Pago:
    - Verificación de asientos libres con SELECT FOR UPDATE (concurrencia).
    - Creación de Venta + Tickets dentro de transacción atómica.
    - Generación de QR para cada ticket.
"""

from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from sistema_cine.models import Funcion, Asiento, Venta, Ticket
from servicios.qr_service import generar_qr_ticket


def confirmar_compra(request, compra):
    """
    Lógica compartida para confirmar una compra una vez que el pago fue aprobado.
    Verifica asientos libres, crea Venta + Tickets + QR.

    Args:
        request: HttpRequest (para obtener el usuario y limpiar sesión).
        compra: dict con 'funcion_id', 'asientos_ids', 'monto_total'.

    Returns:
        dict con 'status' y datos adicionales.
    """
    funcion = get_object_or_404(Funcion, id=compra['funcion_id'])
    asientos_ids = compra['asientos_ids']
    monto_total = Decimal(compra['monto_total'])

    try:
        with transaction.atomic():
            # ─── BARRERA 2: Verificar asientos libres dentro de transacción ───
            asientos_ocupados = list(
                Ticket.objects.filter(
                    funcion=funcion,
                    asiento_id__in=asientos_ids
                ).select_for_update().values_list('asiento_id', flat=True)
            )

            if asientos_ocupados:
                raise IntegrityError("Asientos ocupados")

            # Crear Venta
            venta = Venta.objects.create(
                usuario=request.user,
                monto_total=monto_total,
                metodo_pago='mercado_pago',
                estado_pago='aprobado',
            )

            # Crear Tickets
            asientos = Asiento.objects.filter(id__in=asientos_ids)
            tickets_creados = []
            for asiento in asientos:
                ticket = Ticket.objects.create(
                    venta=venta,
                    funcion=funcion,
                    asiento=asiento,
                    estado_uso='pendiente',
                )
                tickets_creados.append(ticket)

        # Generar QR fuera del atomic
        for ticket in tickets_creados:
            generar_qr_ticket(ticket)

        # Limpiar sesión
        if 'compra_pendiente' in request.session:
            del request.session['compra_pendiente']

        return {
            'status': 'approved',
            'mensaje': '¡Pago exitoso! Tus tickets están listos.',
            'venta_id': venta.id_venta,
            'redirect_url': f'/compras/venta/{venta.id_venta}/tickets/',
        }

    except IntegrityError:
        if 'compra_pendiente' in request.session:
            del request.session['compra_pendiente']
        return {
            'status': 'seats_taken',
            'mensaje': 'Los asientos fueron comprados por otro usuario mientras pagabas.',
        }
