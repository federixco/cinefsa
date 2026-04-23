"""
urls_panel.py — URLs del panel interno de administración del complejo.

Aquí se registran las rutas del panel de gestión:
    /panel/salas/                   → Lista de salas.
    /panel/salas/<id>/editor/       → Editor dinámico de layout.
    /panel/salas/<id>/guardar-layout/ → Endpoint AJAX para guardar layout.
"""

from django.urls import path


# app_name: Namespace para las URLs del panel.
# Permite referenciar las URLs con {% url 'panel:nombre_url' %} en las plantillas.
app_name = 'panel'

urlpatterns = [
    # Las URLs se irán agregando a medida que se construyan las vistas.
]
