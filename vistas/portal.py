"""
portal.py — Vistas públicas del portal del cliente.

Implementa las páginas accesibles sin autenticación:
    - inicio_view: Página principal con cartelera de películas.

Estas vistas NO requieren login. Cualquier visitante puede ver la cartelera.
El login solo se exige para acciones transaccionales (compra de tickets).
"""

from django.shortcuts import render
from django.utils import timezone
from django.db import connection
from sistema_cine.models import Pelicula, Genero, Funcion


def inicio_view(request):
    """
    Página principal del portal CineFSA.

    Carga:
        - peliculas_cartelera: Películas que tienen al menos una función programada
          con fecha >= hoy. Son las que están "en cartelera" actualmente.
        - pelicula_destacada: La primera película de la cartelera (para el hero section).
        - generos: Todos los géneros disponibles (para los filtros).
        - filtro_genero: ID del género seleccionado (si se filtró).
        - peliculas_proximamente: Películas sin funciones programadas (próximos estrenos).
    """
    # Lógica de fechas (Hoy + 6 días)
    from django.db.models import Prefetch
    import datetime
    
    hoy = timezone.localdate()
    fecha_limite = hoy + datetime.timedelta(days=6) # 7 días en total
    
    # Generar la lista de fechas para el frontend
    dias_slider = [hoy + datetime.timedelta(days=i) for i in range(7)]

    from django.db.models.expressions import RawSQL
    # Filtramos funciones que ocurren en los próximos 7 días
    # Inyectamos la función MySQL 'fn_asientos_disponibles' directamente en la consulta ORM
    funciones_activas = Funcion.objects.filter(
        fecha__gte=hoy,
        fecha__lte=fecha_limite
    ).annotate(
        asientos_libres=RawSQL("fn_asientos_disponibles(funcion.id)", [])
    ).order_by('fecha', 'hora_inicio')
    
    ids_peliculas_con_funcion = Funcion.objects.filter(
        fecha__gte=hoy,
        fecha__lte=fecha_limite
    ).values_list('pelicula_id', flat=True).distinct()
    
    peliculas_cartelera = Pelicula.objects.filter(
        id__in=ids_peliculas_con_funcion
    ).prefetch_related('generos', Prefetch('funciones', queryset=funciones_activas))

    # Filtro por género (opcional, via GET)
    filtro_genero = request.GET.get('genero', '')
    if filtro_genero:
        try:
            peliculas_cartelera = peliculas_cartelera.filter(
                generos__id=int(filtro_genero)
            ).distinct()
        except (ValueError, TypeError):
            filtro_genero = ''

    # Películas destacadas para el Hero Carousel (máximo 4)
    peliculas_destacadas = peliculas_cartelera[:4]

    # Películas próximamente (estado='proximamente')
    peliculas_proximamente = Pelicula.objects.filter(
        estado='proximamente'
    ).prefetch_related('generos')

    # Todos los géneros (para los filtros)
    generos = Genero.objects.all()

    return render(request, 'portal/inicio.html', {
        'peliculas_cartelera': peliculas_cartelera,
        'peliculas_destacadas': peliculas_destacadas,
        'peliculas_proximamente': peliculas_proximamente,
        'generos': generos,
        'filtro_genero': filtro_genero,
        'dias_slider': dias_slider,
        'titulo_pagina': 'Cartelera',
    })
