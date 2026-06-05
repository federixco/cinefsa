"""
setup_inicial.py — Script de carga inicial de datos para CineFSA.

Crea:
    1. Usuario administrador por defecto (admin@cinefsa.com / admin1234)
    2. Géneros cinematográficos estándar
    3. Registro de Administrador vinculado al usuario creado
"""
import os
import sys
import django

# Configurar Django antes de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.configuracion')
django.setup()

from sistema_cine.models import Usuario, Administrador, Genero


def crear_admin():
    """Crea el usuario administrador por defecto si no existe."""
    EMAIL    = 'admin@cinefsa.com'
    PASSWORD = 'admin1234'
    USERNAME = 'admin'
    NOMBRE   = 'Administrador CineFSA'

    if Usuario.objects.filter(email=EMAIL).exists():
        print(f'[INFO] El admin "{EMAIL}" ya existe, se omite creación.')
        usuario = Usuario.objects.get(email=EMAIL)
    else:
        usuario = Usuario.objects.create_superuser(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD,
            nombre_completo=NOMBRE,
        )
        print(f'[OK] Usuario administrador creado: {EMAIL} / {PASSWORD}')

    # Crear registro en tabla Administrador si no existe
    if not Administrador.objects.filter(usuario_id_usuario=usuario).exists():
        Administrador.objects.create(
            usuario_id_usuario=usuario,
            nivel_gestion='gerente'
        )
        print('[OK] Registro de Administrador vinculado correctamente.')
    else:
        print('[INFO] Registro de Administrador ya existe.')


def cargar_generos():
    """Carga los géneros cinematográficos estándar si no existen."""
    generos = [
        'Acción',
        'Aventura',
        'Animación',
        'Ciencia ficción',
        'Comedia',
        'Drama',
        'Fantasía',
        'Horror',
        'Misterio',
        'Romance',
        'Suspenso',
        'Terror',
        'Thriller',
        'Documental',
        'Familiar',
    ]

    creados = 0
    for nombre in generos:
        obj, creado = Genero.objects.get_or_create(descripcion=nombre)
        if creado:
            print(f'  [+] Género creado: {nombre}')
            creados += 1

    if creados == 0:
        print('[INFO] Todos los géneros ya existían.')
    else:
        print(f'[OK] {creados} géneros cargados correctamente.')


if __name__ == '__main__':
    print('=' * 60)
    print('   CARGA INICIAL DE DATOS - CineFSA')
    print('=' * 60)

    print('\n--- Creando usuario administrador ---')
    crear_admin()

    print('\n--- Cargando géneros cinematográficos ---')
    cargar_generos()

    print('\n[LISTO] Podés ingresar al sistema con:')
    print('   Email:    admin@cinefsa.com')
    print('   Password: admin1234')
    print('   URL:      http://127.0.0.1:8000/auth/login/')
