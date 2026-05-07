"""
urls.py — Tabla de enrutamiento principal del proyecto.

Aquí se definen todas las rutas (URLs) del sistema. Cada URL se asocia a una vista
que procesa la petición HTTP y devuelve una respuesta (HTML, JSON, etc.).

Estructura de URLs del proyecto:
    /                   → Redirige al portal o al login según estado de sesión.
    /admin/             → Panel de administración automático de Django.
    /auth/              → Autenticación: login, registro, logout, historial (RF-C01).
    /panel/             → URLs del panel interno (editor de salas, cartelera, etc.).
    /multimedia/...     → Archivos subidos (pósters, QR) — solo en desarrollo.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def inicio_redirect(request):
    """
    Vista raíz del sitio (/).

    Redirige al usuario según su estado de autenticación:
        - Si está logueado → historial de transacciones.
        - Si no está logueado → página de login.

    Esta vista es temporal y será reemplazada por el portal del cliente
    cuando se implemente el módulo RF-C02 (Compra Online).
    """
    if request.user.is_authenticated:
        return redirect('autenticacion:historial')
    return redirect('autenticacion:login')


urlpatterns = [
    # Página de inicio: redirige según estado de sesión.
    path('', inicio_redirect, name='inicio'),

    # Panel de administración nativo de Django.
    # Útil para gestión rápida de datos durante el desarrollo.
    path('admin/', admin.site.urls),

    # URLs de autenticación (RF-C01): login, registro, logout, historial.
    path('auth/', include('vistas.urls_autenticacion')),

    # URLs del panel interno del complejo cinematográfico.
    # Incluye: editor de salas, gestión de cartelera, validador QR, etc.
    path('panel/', include('vistas.urls_panel')),
]

# ─── SERVIR ARCHIVOS MULTIMEDIA EN DESARROLLO ─────────────────────────────────
# En producción, el servidor web (Apache/Nginx) se encarga de servir estos archivos.
# En desarrollo (DEBUG=True), Django los sirve directamente para facilitar las pruebas.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
