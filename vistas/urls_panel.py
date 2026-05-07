"""
urls_panel.py — URLs del panel interno de administración del complejo.

Aquí se registran las rutas del panel de gestión:
    /panel/salas/                       → Lista de salas (RF-A01).
    /panel/salas/<id>/editor/           → Editor dinámico de layout (RF-A01).
    /panel/salas/<id>/guardar-layout/   → Endpoint AJAX para guardar layout (RF-A01).
    /panel/usuarios/                    → Gestión de usuarios y roles (RF-A05).
    /panel/usuarios/asignar/            → Asignar rol de empleado (RF-A05).
    /panel/usuarios/revocar/            → Revocar rol de empleado (RF-A05).
"""

from django.urls import path
from vistas.editor_sala import lista_salas, editor_sala, guardar_layout
from vistas.panel.gestion_usuarios import (
    panel_usuarios_view,
    asignar_empleado_view,
    revocar_empleado_view,
)

# app_name: Namespace para las URLs del panel.
# Permite referenciar las URLs con {% url 'panel:nombre_url' %} en las plantillas.
app_name = 'panel'

urlpatterns = [
    # ── RF-A01: Editor Dinámico de Salas ──────────────────────────────────────
    path('salas/', lista_salas, name='lista_salas'),
    path('salas/<int:sala_id>/editor/', editor_sala, name='editor_sala'),
    path('salas/<int:sala_id>/guardar-layout/', guardar_layout, name='guardar_layout'),

    # ── RF-A05: Gestión de Usuarios y Permisos ───────────────────────────────
    path('usuarios/', panel_usuarios_view, name='gestion_usuarios'),
    path('usuarios/asignar/', asignar_empleado_view, name='asignar_empleado'),
    path('usuarios/revocar/', revocar_empleado_view, name='revocar_empleado'),
]
