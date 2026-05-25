from django.urls import path
from .portal_compras import seleccion_asientos_view, procesar_pago_view

app_name = 'compras'

urlpatterns = [
    path('funcion/<int:funcion_id>/asientos/', seleccion_asientos_view, name='seleccion_asientos'),
    path('funcion/<int:funcion_id>/pagar/', procesar_pago_view, name='procesar_pago'),
]
