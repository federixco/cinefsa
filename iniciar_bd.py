"""
iniciar_bd.py - Script de inicializacion automatica de la base de datos.

Este script automatiza la puesta en marcha del proyecto en cualquier computadora:
    1. Conecta al servidor MySQL de XAMPP (root, sin contraseña, puerto 3306).
    2. Crea la base de datos 'sistema_cine' si no existe.
    3. Ejecuta las migraciones de Django para generar todas las tablas.

Uso:
    python iniciar_bd.py

Requisitos previos:
    - MySQL de XAMPP debe estar corriendo.
    - El entorno virtual (venv) debe estar activado.
    - Las dependencias deben estar instaladas (pip install -r requirements.txt o las 4 dependencias).
"""

import os
import sys
import subprocess


def crear_base_de_datos():
    """
    Conecta a MySQL y crea la base de datos 'sistema_cine' si no existe.
    Usa el conector MySQLdb (provisto por la dependencia mysqlclient).
    """
    try:
        import MySQLdb
    except ImportError:
        print("ERROR: No se encontro 'mysqlclient'. Instalalo con:")
        print("  pip install mysqlclient")
        sys.exit(1)

    print("--- Conectando a MySQL (XAMPP) ---")

    try:
        conexion = MySQLdb.connect(
            host='127.0.0.1',
            user='root',
            passwd='',
            port=3306,
        )
        cursor = conexion.cursor()

        # Crear la base de datos con codificacion UTF-8 completa (soporte espanol + emojis).
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS sistema_cine "
            "CHARACTER SET utf8mb4 "
            "COLLATE utf8mb4_unicode_ci"
        )

        print("[OK] Base de datos 'sistema_cine' verificada/creada correctamente.")
        conexion.close()

    except MySQLdb.OperationalError as e:
        print(f"ERROR al conectar a MySQL: {e}")
        print("\nVerifica que:")
        print("  1. XAMPP este abierto y MySQL este corriendo (luz verde).")
        print("  2. El puerto 3306 no este ocupado por otro servicio.")
        sys.exit(1)


def ejecutar_migraciones():
    """
    Ejecuta 'manage.py makemigrations' y 'manage.py migrate' para crear
    todas las tablas en la base de datos a partir de los modelos Django.
    """
    print("\n--- Generando migraciones ---")
    resultado = subprocess.run(
        [sys.executable, 'manage.py', 'makemigrations', 'sistema_cine'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if resultado.returncode != 0:
        print("ERROR al generar migraciones.")
        sys.exit(1)

    print("\n--- Aplicando migraciones a la base de datos ---")
    resultado = subprocess.run(
        [sys.executable, 'manage.py', 'migrate'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if resultado.returncode != 0:
        print("ERROR al aplicar migraciones.")
        sys.exit(1)

    print("\n[OK] Todas las tablas fueron creadas correctamente en MySQL.")


if __name__ == '__main__':
    print("=" * 62)
    print("   INICIALIZACION DE BASE DE DATOS - CineFSA")
    print("=" * 62 + "\n")

    # Configurar la variable de entorno para que Django encuentre la configuracion.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.configuracion')

    crear_base_de_datos()
    ejecutar_migraciones()

    print("\n--- Listo! ---")
    print("Podes iniciar el servidor de desarrollo con:")
    print("  python manage.py runserver")
