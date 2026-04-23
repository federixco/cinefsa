"""
apps.py — Configuración de la aplicación principal 'sistema_cine'.

Django necesita este archivo para registrar la app en INSTALLED_APPS.
Aquí se define el nombre de la app y su ruta de modelos personalizada.

NOTA IMPORTANTE:
El proyecto usa una estructura de carpetas en español (modelos/, vistas/, plantillas/)
en lugar de la estructura estándar de Django (models.py, views.py, templates/).
Por eso, se importan los modelos desde 'modelos/' a través de 'sistema_cine/models.py',
que actúa como puente de re-exportación.
"""

from django.apps import AppConfig


class SistemaCineConfig(AppConfig):
    """Configuración de la app principal del sistema cinematográfico."""

    # default_auto_field: Tipo de clave primaria automática para los modelos de esta app.
    default_auto_field = 'django.db.models.BigAutoField'

    # name: Nombre técnico de la app (debe coincidir con el nombre en INSTALLED_APPS).
    name = 'sistema_cine'

    # verbose_name: Nombre legible que aparece en el panel de administración de Django.
    verbose_name = 'Sistema de Cine'
