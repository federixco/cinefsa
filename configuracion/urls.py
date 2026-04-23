"""
urls.py — Tabla de enrutamiento principal del proyecto.

Aquí se definen todas las rutas (URLs) del sistema. Cada URL se asocia a una vista
que procesa la petición HTTP y devuelve una respuesta (HTML, JSON, etc.).

Estructura de URLs del proyecto:
    /admin/             → Panel de administración automático de Django.
    /panel/             → URLs del panel interno (editor de salas, cartelera, etc.).
    /multimedia/...     → Archivos subidos (pósters, QR) — solo en desarrollo.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Panel de administración nativo de Django.
    # Útil para gestión rápida de datos durante el desarrollo.
    path('admin/', admin.site.urls),

    # URLs del panel interno del complejo cinematográfico.
    # Incluye: editor de salas, gestión de cartelera, validador QR, etc.
    path('panel/', include('vistas.urls_panel')),
]

# ─── SERVIR ARCHIVOS MULTIMEDIA EN DESARROLLO ─────────────────────────────────
# En producción, el servidor web (Apache/Nginx) se encarga de servir estos archivos.
# En desarrollo (DEBUG=True), Django los sirve directamente para facilitar las pruebas.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
