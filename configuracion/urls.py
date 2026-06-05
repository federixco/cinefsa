"""
urls.py — Tabla de enrutamiento principal del proyecto.

Aquí se definen todas las rutas (URLs) del sistema. Cada URL se asocia a una vista
que procesa la petición HTTP y devuelve una respuesta (HTML, JSON, etc.).

Estructura de URLs del proyecto:
    /                   → Página de inicio con cartelera.
    /admin/             → Panel de administración automático de Django.
    /auth/              → Autenticación: login, registro, logout, historial (RF-C01).
    /panel/             → URLs del panel interno (editor de salas, cartelera, etc.).
    /compras/           → Compra de tickets y pagos (RF-C02).
    /cine-club/         → Portal de votación Cine Club (RF-C04).
    /multimedia/...     → Archivos subidos (pósters, QR) — solo en desarrollo.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from vistas.portal import inicio_view
# ── RF-C04: Módulo de votación Cine Club ─────────────────────────────────────
from vistas.votacion import votacion_view, emitir_voto_view


urlpatterns = [
    # Página de inicio: portal público con cartelera.
    path('', inicio_view, name='inicio'),

    # Panel de administración nativo de Django.
    path('admin/', admin.site.urls),

    # URLs de autenticación (RF-C01): login, registro, logout, historial.
    path('auth/', include('vistas.autenticacion.urls')),

    # URLs del panel interno del complejo cinematográfico.
    path('panel/', include('vistas.panel.urls')),

    # ── RF-C04: Portal de votación Cine Club ─────────────────────────────────
    path('cine-club/', votacion_view, name='cine_club'),
    path('cine-club/<int:encuesta_id>/votar/', emitir_voto_view, name='emitir_voto'),

    # URLs de compras y tickets
    path('compras/', include('vistas.compras.urls')),
]

# ─── SERVIR ARCHIVOS MULTIMEDIA EN DESARROLLO ─────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
