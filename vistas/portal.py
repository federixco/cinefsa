"""
portal.py — Vistas públicas del portal del cliente.

Implementa las páginas accesibles sin autenticación:
    - inicio_view: Página principal con cartelera de películas.

Estas vistas NO requieren login. Cualquier visitante puede ver la cartelera.
El login solo se exige para acciones transaccionales (compra de tickets).
"""

from django.shortcuts import render
from django.utils import timezone
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
    hoy = timezone.now().date()

    # IDs de películas que tienen funciones programadas hoy o en el futuro
    ids_peliculas_con_funcion = Funcion.objects.filter(
        fecha__gte=hoy
    ).values_list('pelicula_id', flat=True).distinct()

    # Películas en cartelera (con funciones activas)
    peliculas_cartelera = Pelicula.objects.filter(
        id__in=ids_peliculas_con_funcion
    ).prefetch_related('generos')

    # Filtro por género (opcional, via GET)
    filtro_genero = request.GET.get('genero', '')
    if filtro_genero:
        try:
            peliculas_cartelera = peliculas_cartelera.filter(
                generos__id=int(filtro_genero)
            ).distinct()
        except (ValueError, TypeError):
            filtro_genero = ''

    # Película destacada para el hero (la primera de la cartelera)
    pelicula_destacada = peliculas_cartelera.first()

    # Películas sin funciones (próximamente)
    peliculas_proximamente = Pelicula.objects.exclude(
        id__in=ids_peliculas_con_funcion
    ).prefetch_related('generos')

    # Todos los géneros (para los filtros)
    generos = Genero.objects.all()

    return render(request, 'portal_cliente/inicio.html', {
        'peliculas_cartelera': peliculas_cartelera,
        'pelicula_destacada': pelicula_destacada,
        'peliculas_proximamente': peliculas_proximamente,
        'generos': generos,
        'filtro_genero': filtro_genero,
        'titulo_pagina': 'Cartelera',
    })
