#!/usr/bin/env python
"""
manage.py — Punto de entrada de línea de comandos de Django.

Este script permite ejecutar todos los comandos administrativos del proyecto:
    python manage.py runserver        → Inicia el servidor de desarrollo.
    python manage.py makemigrations   → Genera archivos de migración a partir de los modelos.
    python manage.py migrate          → Ejecuta las migraciones en la base de datos MySQL.
    python manage.py createsuperuser  → Crea un usuario administrador para el panel /admin/.

La variable DJANGO_SETTINGS_MODULE apunta al archivo de configuración principal:
configuracion/configuracion.py
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.configuracion')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y disponible en el "
            "entorno virtual (venv)? Activá el entorno con: .\\venv\\Scripts\\activate"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
