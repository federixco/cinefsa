"""
urls_panel.py — URLs del panel interno de administración del complejo.

Aquí se registran las rutas del panel de gestión:
    /panel/salas/                   → Lista de salas.
    /panel/salas/<id>/editor/       → Editor dinámico de layout.
    /panel/salas/<id>/guardar-layout/ → Endpoint AJAX para guardar layout.
"""

from django.urls import path
from vistas.editor_sala import lista_salas, editor_sala, guardar_layout

# app_name: Namespace para las URLs del panel.
# Permite referenciar las URLs con {% url 'panel:nombre_url' %} en las plantillas.
app_name = 'panel'

urlpatterns = [
    # URL: /panel/salas/
    path('salas/', lista_salas, name='lista_salas'),
    # URL: /panel/salas/1/editor/
    path('salas/<int:sala_id>/editor/', editor_sala, name='editor_sala'),
    # URL: /panel/salas/1/guardar-layout/
    path('salas/<int:sala_id>/guardar-layout/', guardar_layout, name='guardar_layout'),
]
