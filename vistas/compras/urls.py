"""
urls_compras.py — URLs del módulo de compras y tickets.

Rutas:
    /compras/funcion/<id>/asientos/     → Selección de asientos (mapa de sala).
    /compras/funcion/<id>/pagar/        → Crear preferencia MP + retornar URL.
    /compras/verificar-pago/            → AJAX: buscar pago en API de MP.
    /compras/venta/<id>/tickets/        → Ver tickets generados con QR.
"""

from django.urls import path
from .views import (
    seleccion_asientos_view,
    procesar_pago_view,
    procesar_pago_efectivo_view,
    verificar_pago_view,
    ver_tickets_view,
)

app_name = 'compras'

urlpatterns = [
    path('funcion/<int:funcion_id>/asientos/', seleccion_asientos_view, name='seleccion_asientos'),
    path('funcion/<int:funcion_id>/pagar/', procesar_pago_view, name='procesar_pago'),
    path('funcion/<int:funcion_id>/pagar-efectivo/', procesar_pago_efectivo_view, name='procesar_pago_efectivo'),
    path('verificar-pago/', verificar_pago_view, name='verificar_pago'),
    path('venta/<int:venta_id>/tickets/', ver_tickets_view, name='ver_tickets'),
]
