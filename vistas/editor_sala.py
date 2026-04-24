from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from sistema_cine.models import Sala, Asiento

def lista_salas(request):
    """
    Vista que lista todas las salas del complejo.
    Permite acceder al editor de layout de cada una.
    """
    # Obtenemos todas las salas de la base de datos, ordenadas por nombre.
    salas = Sala.objects.all().order_by('nombre_sala')
    
    return render(request, 'panel_interno/lista_salas.html', {
        'salas': salas
    })

def editor_sala(request, sala_id):
    """
    Renderiza la interfaz del editor visual para una sala específica.
    """
    sala = get_object_or_404(Sala, id=sala_id)
    return render(request, 'panel_interno/editor_sala.html', {
        'sala': sala
    })

@require_POST
def guardar_layout(request, sala_id):
    """
    Endpoint AJAX para recibir el JSON con la grilla y crear/actualizar 
    los Asientos en la base de datos.
    """
    sala = get_object_or_404(Sala, id=sala_id)
    
    try:
        data = json.loads(request.body)
        filas = data.get('filas')
        columnas = data.get('columnas')
        asientos_data = data.get('asientos', [])
        
        # 1. Actualizar la capacidad de la sala automáticamente según el diseño
        sala.capacidad_maxima = len(asientos_data)
            
        # 2. Guardar el JSON crudo en la sala (para cargar rápido el frontend la próxima vez)
        sala.layout_config = data
        sala.save()
        
        # 3. Sincronizar Asientos en la BD (Módulo de Infraestructura)
        # Por simplicidad, borramos los asientos actuales de la sala y creamos los nuevos.
        # En un sistema en producción con ventas, se debe actualizar y verificar que no tengan tickets.
        sala.asientos.all().delete()
        
        nuevos_asientos = []
        for a in asientos_data:
            nuevos_asientos.append(
                Asiento(
                    sala=sala,
                    fila=str(a['fila']),
                    columna=a['columna'],
                    tipo=a['tipo'],
                    estado='disponible'
                )
            )
            
        # bulk_create hace 1 sola consulta SQL INSERT grande, súper rápido.
        Asiento.objects.bulk_create(nuevos_asientos)
        
        return JsonResponse({'status': 'ok', 'mensaje': 'Layout guardado con éxito'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

