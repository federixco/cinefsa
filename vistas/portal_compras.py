import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from sistema_cine.models import Funcion, Asiento, Venta, Ticket

@login_required
def seleccion_asientos_view(request, funcion_id):
    """
    Renderiza la sala y sus asientos para una función específica.
    Pinta de rojo o deshabilita los asientos que ya tienen un Ticket asociado.
    """
    funcion = get_object_or_404(Funcion, id_funcion=funcion_id)
    sala = funcion.sala
    
    # Todos los asientos físicos de la sala
    asientos = sala.asientos.all()
    
    # Buscar qué asientos ya fueron vendidos para ESTA función en particular.
    # Obtiene una lista rápida de los IDs de los asientos ocupados.
    asientos_ocupados_ids = Ticket.objects.filter(
        funcion=funcion
    ).values_list('asiento_id_asiento', flat=True)
    
    # El layout de la sala está guardado en sala.layout_config (JSON)
    layout = sala.layout_config if sala.layout_config else {}

    return render(request, 'portal_cliente/seleccion_asientos.html', {
        'funcion': funcion,
        'sala': sala,
        'layout': json.dumps(layout),
        'asientos_ocupados': list(asientos_ocupados_ids),
        'asientos_totales': asientos
    })

@login_required
@require_POST
def procesar_pago_view(request, funcion_id):
    """
    Endpoint para procesar la compra final.
    Acá implementamos la DEFENSA DE NIVEL 2 (transaction.atomic).
    """
    funcion = get_object_or_404(Funcion, id_funcion=funcion_id)
    
    # Suponemos que el frontend nos manda por POST un JSON con los IDs de asientos y el método de pago
    try:
        data = json.loads(request.body)
        asientos_seleccionados_ids = data.get('asientos_ids', [])
        metodo_pago = data.get('metodo_pago', 'mercado_pago')
        
        if not asientos_seleccionados_ids:
            return JsonResponse({'error': 'No seleccionó ningún asiento.'}, status=400)
            
        asientos = Asiento.objects.filter(id_asiento__in=asientos_seleccionados_ids)
        if asientos.count() != len(asientos_seleccionados_ids):
            return JsonResponse({'error': 'Algunos asientos no son válidos.'}, status=400)
            
        monto_total = len(asientos) * funcion.precio_entrada
        
        # EL BLOQUE MÁGICO: TODO O NADA
        with transaction.atomic():
            # 1. Crear la cabecera de la Venta
            venta = Venta.objects.create(
                usuario=request.user,
                monto_total=monto_total,
                metodo_pago=metodo_pago,
                estado_pago='aprobado' # Simulación: Pago existoso
            )
            
            # 2. Crear los tickets (El Nivel 1 de defensa actúa acá)
            for asiento in asientos:
                # Si alguien más compró este asiento una fracción de segundo antes,
                # el `unique_together` en MySQL hará que esto lance un IntegrityError.
                Ticket.objects.create(
                    venta=venta,
                    funcion=funcion,
                    asiento=asiento,
                    estado_uso='pendiente'
                )
                
        # Si llegamos acá, la compra fue 100% exitosa y no hubo colisiones.
        return JsonResponse({
            'status': 'ok',
            'mensaje': '¡Compra realizada con éxito!',
            'venta_id': venta.id_venta
        })
        
    except IntegrityError:
        # ATRAJAMOS LA COLISIÓN: El transaction.atomic ya deshizo la creación de la Venta.
        # No se le cobró nada al cliente, la base de datos está intacta.
        return JsonResponse({
            'error': 'Lo sentimos, uno o más asientos acaban de ser ocupados por otra persona. Por favor, volvé a intentarlo.'
        }, status=409) # 409 Conflict
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
