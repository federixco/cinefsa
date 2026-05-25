import json
import qrcode
import os
import zipfile
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.conf import settings

from sistema_cine.models import Funcion, Asiento, Venta, Ticket

@login_required
def seleccion_asientos_view(request, funcion_id):
    """
    Renderiza la sala y sus asientos para una función específica.
    Pinta de rojo o deshabilita los asientos que ya tienen un Ticket asociado.
    """
    funcion = get_object_or_404(Funcion, id=funcion_id)
    sala = funcion.sala
    
    # Todos los asientos físicos de la sala
    asientos = sala.asientos.all()
    
    # Buscar qué asientos ya fueron vendidos para ESTA función en particular.
    asientos_ocupados_ids = Ticket.objects.filter(
        funcion=funcion
    ).values_list('asiento_id', flat=True)
    
    # El layout de la sala está guardado en sala.layout_config (JSON)
    layout = sala.layout_config if sala.layout_config else {}

    return render(request, 'portal_cliente/seleccion_asientos.html', {
        'funcion': funcion,
        'sala': sala,
        'layout': json.dumps(layout),
        'asientos_ocupados': list(asientos_ocupados_ids),
        'asientos_totales': asientos
    })


def _generar_qr_ticket(ticket):
    """
    Genera una imagen QR para un ticket y la guarda en el campo imagen_qr.
    El contenido del QR es el código UUID único del ticket.
    """
    # Contenido del QR: código único del ticket
    contenido_qr = f"CINEFSA-TICKET-{ticket.codigo_qr}"
    
    # Generar imagen QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(contenido_qr)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en memoria y luego al campo ImageField
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    nombre_archivo = f"ticket_{ticket.id_ticket}_{ticket.codigo_qr}.png"
    ticket.imagen_qr.save(nombre_archivo, ContentFile(buffer.read()), save=True)


@login_required
@require_POST
def procesar_pago_view(request, funcion_id):
    """
    Endpoint para procesar la compra final.
    Crea la Venta, los Tickets y genera las imágenes QR.
    """
    funcion = get_object_or_404(Funcion, id=funcion_id)
    
    try:
        data = json.loads(request.body)
        asientos_seleccionados_ids = data.get('asientos_ids', [])
        metodo_pago = data.get('metodo_pago', 'mercado_pago')
        
        if not asientos_seleccionados_ids:
            return JsonResponse({'error': 'No seleccionó ningún asiento.'}, status=400)
            
        asientos = Asiento.objects.filter(id__in=asientos_seleccionados_ids)
        if asientos.count() != len(asientos_seleccionados_ids):
            return JsonResponse({'error': 'Algunos asientos no son válidos.'}, status=400)
            
        monto_total = len(asientos) * funcion.precio_entrada
        
        # TRANSACCIÓN ATÓMICA: TODO O NADA
        with transaction.atomic():
            # 1. Crear la cabecera de la Venta
            venta = Venta.objects.create(
                usuario=request.user,
                monto_total=monto_total,
                metodo_pago=metodo_pago,
                estado_pago='aprobado'  # Simulación: Pago exitoso
            )
            
            # 2. Crear los tickets
            tickets_creados = []
            for asiento in asientos:
                ticket = Ticket.objects.create(
                    venta=venta,
                    funcion=funcion,
                    asiento=asiento,
                    estado_uso='pendiente'
                )
                tickets_creados.append(ticket)
        
        # 3. Generar QR para cada ticket (fuera del atomic para no bloquear la BD)
        for ticket in tickets_creados:
            _generar_qr_ticket(ticket)
                
        # Redirigir a la página de tickets
        return JsonResponse({
            'status': 'ok',
            'mensaje': '¡Compra realizada con éxito!',
            'venta_id': venta.id_venta,
            'redirect_url': f'/compras/venta/{venta.id_venta}/tickets/'
        })
        
    except IntegrityError:
        return JsonResponse({
            'error': 'Lo sentimos, uno o más asientos acaban de ser ocupados por otra persona. Por favor, volvé a intentarlo.'
        }, status=409)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def ver_tickets_view(request, venta_id):
    """
    Muestra los tickets generados de una venta con sus códigos QR.
    Solo el usuario dueño de la venta puede verlos.
    """
    venta = get_object_or_404(Venta, id_venta=venta_id, usuario=request.user)
    tickets = venta.tickets.select_related('funcion__pelicula', 'asiento', 'funcion__sala')
    
    return render(request, 'portal_cliente/ver_tickets.html', {
        'venta': venta,
        'tickets': tickets,
        'titulo_pagina': f'Tickets - Venta #{venta.id_venta}',
    })


@login_required
def descargar_qr_ticket(request, ticket_id):
    """
    Descarga la imagen QR de un ticket individual como PNG.
    Solo el dueño del ticket puede descargarlo.
    """
    ticket = get_object_or_404(Ticket, id_ticket=ticket_id, venta__usuario=request.user)
    
    if not ticket.imagen_qr:
        raise Http404("Este ticket no tiene QR generado.")
    
    # Leer el archivo y devolverlo como descarga
    response = HttpResponse(ticket.imagen_qr.read(), content_type='image/png')
    nombre_archivo = f"CineFSA_Ticket_{ticket.id_ticket}_{ticket.asiento.fila}{ticket.asiento.numero}.png"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


@login_required
def descargar_qr_venta(request, venta_id):
    """
    Descarga todos los QR de una venta en un archivo ZIP.
    Solo el dueño de la venta puede descargarlo.
    """
    venta = get_object_or_404(Venta, id_venta=venta_id, usuario=request.user)
    tickets = venta.tickets.select_related('funcion__pelicula', 'asiento')
    
    # Crear ZIP en memoria
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for ticket in tickets:
            if ticket.imagen_qr:
                nombre = f"Ticket_{ticket.id_ticket}_{ticket.asiento.fila}{ticket.asiento.numero}.png"
                zf.writestr(nombre, ticket.imagen_qr.read())
    
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="CineFSA_Venta_{venta.id_venta}_QRs.zip"'
    return response
