"""
urls_panel.py — URLs del panel interno de administración del complejo.

<<<<<<< Updated upstream
Aquí se registran las rutas del panel de gestión para el Administrador.

URLs implementadas (RF-A05 — Gestión de Usuarios y Permisos):
    /panel/usuarios/              → Lista de usuarios con buscador y gestión de roles.
    /panel/usuarios/asignar/      → POST: Eleva un usuario al rol de Empleado.
    /panel/usuarios/revocar/      → POST: Revoca el rol de Empleado de un usuario.

Todas las vistas del panel están protegidas por el decorador @solo_administrador,
que verifica que el usuario logueado tenga un registro en la tabla 'administrador'.
"""

from django.urls import path
=======
Aquí se registran las rutas del panel de gestión:

    RF-A01 — Editor Dinámico de Salas:
        /panel/salas/                       → Lista de salas.
        /panel/salas/crear/                 → Crear nueva sala (POST).
        /panel/salas/<id>/editor/           → Editor visual de layout.
        /panel/salas/<id>/guardar-layout/   → Endpoint AJAX guardar layout.
        /panel/salas/<id>/toggle-estado/    → Activar/desactivar sala.

    RF-A05 — Gestión de Usuarios y Permisos:
        /panel/usuarios/                    → Panel de usuarios con buscador.
        /panel/usuarios/asignar/            → Asignar rol empleado (POST).
        /panel/usuarios/revocar/            → Revocar rol empleado (POST).

    RF-A02 — Gestión de Cartelera:
        Géneros:
        /panel/cartelera/generos/                   → Lista + creación rápida.
        /panel/cartelera/generos/crear/             → Crear género (POST).
        /panel/cartelera/generos/<id>/editar/       → Editar género (GET/POST).
        /panel/cartelera/generos/<id>/eliminar/     → Eliminar género (POST).

        Películas:
        /panel/cartelera/peliculas/                 → Lista de películas.
        /panel/cartelera/peliculas/crear/           → Crear película (GET/POST).
        /panel/cartelera/peliculas/<id>/editar/     → Editar película (GET/POST).
        /panel/cartelera/peliculas/<id>/eliminar/   → Eliminar película (POST).

        Funciones:
        /panel/cartelera/funciones/                 → Lista (próximas + historial).
        /panel/cartelera/funciones/crear/           → Programar función (GET/POST).
        /panel/cartelera/funciones/<id>/editar/     → Editar función (GET/POST).
        /panel/cartelera/funciones/<id>/eliminar/   → Eliminar función (POST).

Todas las vistas del panel están protegidas por @solo_administrador.
"""

from django.urls import path

# ── RF-A01: Editor de Salas ───────────────────────────────────────────────────
from vistas.editor_sala import lista_salas, editor_sala, guardar_layout, crear_sala, toggle_estado_sala

# ── RF-A05: Gestión de Usuarios ───────────────────────────────────────────────
>>>>>>> Stashed changes
from vistas.panel.gestion_usuarios import (
    panel_usuarios_view,
    asignar_empleado_view,
    revocar_empleado_view,
)

<<<<<<< Updated upstream

# app_name: Namespace para las URLs del panel.
# Permite referenciar las URLs con {% url 'panel:nombre_url' %} en las plantillas.
app_name = 'panel'

urlpatterns = [

    # ── RF-A05: Gestión de Usuarios y Permisos ────────────────────────────────

    # Panel principal: formulario de búsqueda + tabla de resultados con roles.
    # Método: GET (la búsqueda se realiza con parámetros en la URL: ?busqueda=...)
    path(
        'usuarios/',
        panel_usuarios_view,
        name='gestion_usuarios'
    ),

    # Asignar rol de Empleado a un usuario existente.
    # Método: POST (recibe usuario_id, id_validador y terminal_venta)
    path(
        'usuarios/asignar/',
        asignar_empleado_view,
        name='asignar_empleado'
    ),

    # Revocar el rol de Empleado de un usuario.
    # Método: POST (recibe solo usuario_id)
    path(
        'usuarios/revocar/',
        revocar_empleado_view,
        name='revocar_empleado'
    ),
=======
# ── RF-A02: Gestión de Cartelera ──────────────────────────────────────────────
from vistas.panel.gestion_cartelera import (
    # Géneros
    listar_generos_view,
    crear_genero_view,
    editar_genero_view,
    eliminar_genero_view,
    # Películas
    listar_peliculas_view,
    crear_pelicula_view,
    editar_pelicula_view,
    eliminar_pelicula_view,
    # Funciones
    listar_funciones_view,
    crear_funcion_view,
    editar_funcion_view,
    eliminar_funcion_view,
)


# Namespace del panel. Permite usar {% url 'panel:nombre' %} en las plantillas.
app_name = 'panel'

urlpatterns = [

    # ── RF-A01: Editor Dinámico de Salas ─────────────────────────────────────
    path('salas/',                             lista_salas,        name='lista_salas'),
    path('salas/crear/',                       crear_sala,         name='crear_sala'),
    path('salas/<int:sala_id>/editor/',        editor_sala,        name='editor_sala'),
    path('salas/<int:sala_id>/guardar-layout/',guardar_layout,     name='guardar_layout'),
    path('salas/<int:sala_id>/toggle-estado/', toggle_estado_sala, name='toggle_estado_sala'),

    # ── RF-A05: Gestión de Usuarios y Permisos ───────────────────────────────
    path('usuarios/',          panel_usuarios_view,   name='gestion_usuarios'),
    path('usuarios/asignar/',  asignar_empleado_view, name='asignar_empleado'),
    path('usuarios/revocar/',  revocar_empleado_view, name='revocar_empleado'),

    # ── RF-A02: Gestión de Cartelera — GÉNEROS ───────────────────────────────
    # Lista de géneros + formulario de creación rápida inline
    path('cartelera/generos/',                       listar_generos_view,  name='listar_generos'),
    # Crear género (solo POST desde el formulario del listado)
    path('cartelera/generos/crear/',                 crear_genero_view,    name='crear_genero'),
    # Editar género identificado por su PK entero
    path('cartelera/generos/<int:genero_id>/editar/',   editar_genero_view,  name='editar_genero'),
    # Eliminar género (solo POST con confirmación)
    path('cartelera/generos/<int:genero_id>/eliminar/', eliminar_genero_view,name='eliminar_genero'),

    # ── RF-A02: Gestión de Cartelera — PELÍCULAS ─────────────────────────────
    path('cartelera/peliculas/',                         listar_peliculas_view, name='listar_peliculas'),
    path('cartelera/peliculas/crear/',                   crear_pelicula_view,   name='crear_pelicula'),
    path('cartelera/peliculas/<int:pelicula_id>/editar/',   editar_pelicula_view,  name='editar_pelicula'),
    path('cartelera/peliculas/<int:pelicula_id>/eliminar/', eliminar_pelicula_view,name='eliminar_pelicula'),

    # ── RF-A02: Gestión de Cartelera — FUNCIONES ─────────────────────────────
    path('cartelera/funciones/',                        listar_funciones_view, name='listar_funciones'),
    path('cartelera/funciones/crear/',                  crear_funcion_view,    name='crear_funcion'),
    path('cartelera/funciones/<int:funcion_id>/editar/',   editar_funcion_view,  name='editar_funcion'),
    path('cartelera/funciones/<int:funcion_id>/eliminar/', eliminar_funcion_view,name='eliminar_funcion'),
>>>>>>> Stashed changes

]

