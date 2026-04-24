"""
urls_autenticacion.py — Tabla de enrutamiento del módulo de autenticación.

Define las rutas HTTP para el flujo de autenticación del sistema (RF-C01):
    /auth/login/       → Formulario de inicio de sesión.
    /auth/registro/    → Formulario de registro de nuevos clientes.
    /auth/logout/      → Cierre de sesión (POST).
    /auth/historial/   → Historial de transacciones del usuario logueado.

El namespace 'autenticacion' permite referenciar estas URLs desde las
plantillas con: {% url 'autenticacion:login' %}, {% url 'autenticacion:registro' %}, etc.
"""

from django.urls import path
from vistas.autenticacion.views import (
    login_view,
    registro_view,
    logout_view,
    historial_view,
)


# app_name: Namespace para las URLs de autenticación.
app_name = 'autenticacion'

urlpatterns = [
    # Inicio de sesión: formulario de login con email y contraseña.
    path('login/', login_view, name='login'),

    # Registro: formulario de creación de cuenta nueva (Usuario + Cliente).
    path('registro/', registro_view, name='registro'),

    # Cierre de sesión: destruye la sesión y redirige al login.
    path('logout/', logout_view, name='logout'),

    # Historial: lista de transacciones del usuario logueado.
    path('historial/', historial_view, name='historial'),
]
