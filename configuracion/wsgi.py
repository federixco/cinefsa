"""
wsgi.py — Punto de entrada WSGI para servidores de producción.

WSGI (Web Server Gateway Interface) es el protocolo estándar que conecta
el servidor web (Apache, Nginx + Gunicorn) con la aplicación Django.

En desarrollo no se usa directamente (manage.py runserver tiene su propio servidor).
En producción, el servidor web importa este módulo para atender las peticiones HTTP.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.configuracion')

application = get_wsgi_application()
