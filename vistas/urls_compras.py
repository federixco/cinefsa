from django.urls import path
from .portal_compras import (
    seleccion_asientos_view, procesar_pago_view, ver_tickets_view,
    descargar_qr_ticket
)

app_name = 'compras'

urlpatterns = [
    path('funcion/<int:funcion_id>/asientos/', seleccion_asientos_view, name='seleccion_asientos'),
    path('funcion/<int:funcion_id>/pagar/', procesar_pago_view, name='procesar_pago'),
    path('venta/<int:venta_id>/tickets/', ver_tickets_view, name='ver_tickets'),
    path('ticket/<int:ticket_id>/descargar-qr/', descargar_qr_ticket, name='descargar_qr_ticket'),
]
