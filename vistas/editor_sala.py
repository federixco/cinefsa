"""
editor_sala.py — Vistas del módulo de infraestructura de salas (RF-A01).

Implementa:
    - lista_salas: Listado de todas las salas del complejo.
    - crear_sala: Creación de una nueva sala (POST desde modal).
    - editor_sala: Renderiza el editor visual de layout para una sala.
    - guardar_layout: Endpoint AJAX para persistir el layout diseñado.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
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


@require_POST
def crear_sala(request):
    """
    Vista para crear una nueva sala desde el modal del panel (RF-A01).

    Recibe via POST:
        - nombre_sala: Nombre único de la sala (ej: 'Sala IMAX').
        - estado: 'activa' o 'mantenimiento'.

    La capacidad_maxima se inicializa en 0 y se ajusta automáticamente
    cuando el administrador diseña el layout desde el editor.

    Redirige a la lista de salas con un mensaje de éxito o error.
    """
    nombre = request.POST.get('nombre_sala', '').strip()
    estado = request.POST.get('estado', 'activa')

    # Validación básica
    if not nombre:
        messages.error(request, 'El nombre de la sala es obligatorio.')
        return redirect('panel:lista_salas')

    if Sala.objects.filter(nombre_sala=nombre).exists():
        messages.error(request, f'Ya existe una sala con el nombre "{nombre}".')
        return redirect('panel:lista_salas')

    if estado not in ('activa', 'mantenimiento'):
        estado = 'activa'

    Sala.objects.create(
        nombre_sala=nombre,
        capacidad_maxima=0,
        estado=estado,
    )
    messages.success(request, f'La sala "{nombre}" fue creada. Diseñá su layout para definir la capacidad.')
    return redirect('panel:lista_salas')


@require_POST
def toggle_estado_sala(request, sala_id):
    """
    Vista para alternar el estado de una sala entre 'activa' y 'mantenimiento'.

    Si la sala está activa, pasa a mantenimiento y viceversa.
    Redirige a la lista de salas con un mensaje informativo.
    """
    sala = get_object_or_404(Sala, id=sala_id)

    if sala.estado == 'activa':
        sala.estado = 'mantenimiento'
        msg = f'La sala "{sala.nombre_sala}" fue puesta en mantenimiento.'
    else:
        sala.estado = 'activa'
        msg = f'La sala "{sala.nombre_sala}" fue activada correctamente.'

    sala.save()
    messages.success(request, msg)
    return redirect('panel:lista_salas')


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

    El frontend envía un JSON con la estructura:
        {
            filas: int,
            columnas: int,
            asientos: [
                { fila: int, columna: int, tipo: 'general'|'vip'|'discapacitado' },
                ...
            ]
        }

    Mapeo frontend → modelo Asiento:
        fila    → fila (se convierte a string para letras: 1→'A', 2→'B', etc.)
        columna → numero (número del asiento dentro de la fila)
        tipo    → tipo_asiento ('general', 'vip', 'discapacitado')
        columna → posicion_x (coordenada horizontal en la grilla visual)
        fila    → posicion_y (coordenada vertical en la grilla visual)
    """
    sala = get_object_or_404(Sala, id=sala_id)

    try:
        data = json.loads(request.body)
        asientos_data = data.get('asientos', [])

        # 1. Actualizar la capacidad de la sala según el diseño
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
            fila_num = int(a['fila'])
            col_num = int(a['columna'])
            tipo = a.get('tipo', 'general')

            # Convertir el número de fila a letra (1→A, 2→B, ..., 26→Z)
            fila_letra = chr(64 + fila_num) if fila_num <= 26 else str(fila_num)

            nuevos_asientos.append(
                Asiento(
                    sala=sala,
                    fila=fila_letra,
                    numero=col_num,
                    tipo_asiento=tipo,
                    posicion_x=col_num,
                    posicion_y=fila_num,
                )
            )

        # bulk_create hace 1 sola consulta SQL INSERT grande, súper rápido.
        Asiento.objects.bulk_create(nuevos_asientos)

        return JsonResponse({'status': 'ok', 'mensaje': 'Layout guardado con éxito'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
