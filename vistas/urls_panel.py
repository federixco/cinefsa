"""
urls_panel.py — URLs del panel interno de administración del complejo.

Aquí se registran las rutas del panel de gestión:
    /panel/salas/                       → Lista de salas (RF-A01).
    /panel/salas/<id>/editor/           → Editor dinámico de layout (RF-A01).
    /panel/salas/<id>/guardar-layout/   → Endpoint AJAX para guardar layout (RF-A01).
    /panel/usuarios/                    → Gestión de usuarios y roles (RF-A05).
    /panel/usuarios/asignar/            → Asignar rol de empleado (RF-A05).
    /panel/usuarios/revocar/            → Revocar rol de empleado (RF-A05).
    /panel/cartelera/                   → Módulo de Cartelera (RF-A02).
"""

from django.urls import path

# ── RF-A01: Editor de Salas ───────────────────────────────────────────────────
from vistas.editor_sala import lista_salas, editor_sala, guardar_layout, crear_sala, toggle_estado_sala

# ── RF-A05: Gestión de Usuarios ───────────────────────────────────────────────
from vistas.panel.gestion_usuarios import (
    panel_usuarios_view,
    asignar_empleado_view,
    revocar_empleado_view,
)

# ── RF-A02: Gestión de Cartelera ──────────────────────────────────────────────
from vistas.panel.gestion_cartelera import (
    listar_generos_view,
    editar_genero_view,
    eliminar_genero_view,
    listar_peliculas_view,
    crear_pelicula_view,
    editar_pelicula_view,
    eliminar_pelicula_view,
    listar_funciones_view,
    crear_funcion_view,
    editar_funcion_view,
    eliminar_funcion_view,
)

# ── RF-A04: Monitor de Votaciones ─────────────────────────────────────────────
from vistas.panel.gestion_votaciones import (
    monitor_votaciones_view,
    detalle_encuesta_view,
    crear_encuesta_view,
    editar_encuesta_view,
    toggle_encuesta_view,
    eliminar_encuesta_view,
)

# app_name: Namespace para las URLs del panel.
app_name = 'panel'

urlpatterns = [
    # ── RF-A01: Editor Dinámico de Salas ──────────────────────────────────────
    path('salas/', lista_salas, name='lista_salas'),
    path('salas/crear/', crear_sala, name='crear_sala'),
    path('salas/<int:sala_id>/editor/', editor_sala, name='editor_sala'),
    path('salas/<int:sala_id>/guardar-layout/', guardar_layout, name='guardar_layout'),
    path('salas/<int:sala_id>/toggle-estado/', toggle_estado_sala, name='toggle_estado_sala'),

    # ── RF-A05: Gestión de Usuarios y Permisos ───────────────────────────────
    path('usuarios/', panel_usuarios_view, name='gestion_usuarios'),
    path('usuarios/asignar/', asignar_empleado_view, name='asignar_empleado'),
    path('usuarios/revocar/', revocar_empleado_view, name='revocar_empleado'),

    # ── RF-A02: Gestión de Cartelera — GÉNEROS (solo listar/editar/eliminar) ───────────
    path('cartelera/generos/', listar_generos_view, name='listar_generos'),
    path('cartelera/generos/<int:genero_id>/editar/', editar_genero_view, name='editar_genero'),
    path('cartelera/generos/<int:genero_id>/eliminar/', eliminar_genero_view, name='eliminar_genero'),

    # ── RF-A02: Gestión de Cartelera — PELÍCULAS ─────────────────────────────
    path('cartelera/peliculas/', listar_peliculas_view, name='listar_peliculas'),
    path('cartelera/peliculas/crear/', crear_pelicula_view, name='crear_pelicula'),
    path('cartelera/peliculas/<int:pelicula_id>/editar/', editar_pelicula_view, name='editar_pelicula'),
    path('cartelera/peliculas/<int:pelicula_id>/eliminar/', eliminar_pelicula_view, name='eliminar_pelicula'),

    # ── RF-A02: Gestión de Cartelera — FUNCIONES ─────────────────────────────
    path('cartelera/funciones/', listar_funciones_view, name='listar_funciones'),
    path('cartelera/funciones/crear/', crear_funcion_view, name='crear_funcion'),
    path('cartelera/funciones/<int:funcion_id>/editar/', editar_funcion_view, name='editar_funcion'),
    path('cartelera/funciones/<int:funcion_id>/eliminar/', eliminar_funcion_view, name='eliminar_funcion'),

    # ── RF-A04: Monitor de Votaciones — ENCUESTAS ─────────────────────────────
    path('votaciones/', monitor_votaciones_view, name='monitor_votaciones'),
    path('votaciones/crear/', crear_encuesta_view, name='crear_encuesta'),
    path('votaciones/<int:encuesta_id>/detalle/', detalle_encuesta_view, name='detalle_votacion'),
    path('votaciones/<int:encuesta_id>/editar/', editar_encuesta_view, name='editar_encuesta'),
    path('votaciones/<int:encuesta_id>/toggle/', toggle_encuesta_view, name='toggle_encuesta'),
    path('votaciones/<int:encuesta_id>/eliminar/', eliminar_encuesta_view, name='eliminar_encuesta'),
]
