"""
urls_panel.py — URLs del panel interno de administración del complejo.

Aquí se registran las rutas del panel de gestión para el Administrador.

URLs implementadas (RF-A05 — Gestión de Usuarios y Permisos):
    /panel/usuarios/              → Lista de usuarios con buscador y gestión de roles.
    /panel/usuarios/asignar/      → POST: Eleva un usuario al rol de Empleado.
    /panel/usuarios/revocar/      → POST: Revoca el rol de Empleado de un usuario.

Todas las vistas del panel están protegidas por el decorador @solo_administrador,
que verifica que el usuario logueado tenga un registro en la tabla 'administrador'.
"""

from django.urls import path
from vistas.panel.gestion_usuarios import (
    panel_usuarios_view,
    asignar_empleado_view,
    revocar_empleado_view,
)


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

]
