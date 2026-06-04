"""
urls_compras.py — URLs del módulo de compras y tickets.

Rutas:
    /compras/funcion/<id>/asientos/     → Selección de asientos (mapa de sala).
    /compras/funcion/<id>/pagar/        → Crear preferencia MP + retornar URL.
    /compras/verificar-pago/            → AJAX: buscar pago en API de MP.
    /compras/retorno/                   → Backup: retorno desde MP (producción).
    /compras/venta/<id>/tickets/        → Ver tickets generados con QR.
    /compras/ticket/<id>/descargar-qr/  → Descargar QR individual.
    /compras/ticket/<id>/descargar/     → Descargar ticket completo (Word .docx).
"""

from django.urls import path
from .portal_compras import (
    seleccion_asientos_view,
    procesar_pago_view,
    verificar_pago_view,
    retorno_mercadopago_view,
    ver_tickets_view,
    descargar_qr_ticket,
    descargar_ticket_word,
)

app_name = 'compras'

urlpatterns = [
    path('funcion/<int:funcion_id>/asientos/', seleccion_asientos_view, name='seleccion_asientos'),
    path('funcion/<int:funcion_id>/pagar/', procesar_pago_view, name='procesar_pago'),
    path('verificar-pago/', verificar_pago_view, name='verificar_pago'),
    path('retorno/', retorno_mercadopago_view, name='retorno_mp'),
    path('venta/<int:venta_id>/tickets/', ver_tickets_view, name='ver_tickets'),
    path('ticket/<int:ticket_id>/descargar-qr/', descargar_qr_ticket, name='descargar_qr_ticket'),
    path('ticket/<int:ticket_id>/descargar/', descargar_ticket_word, name='descargar_ticket'),
]
