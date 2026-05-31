"""
mercadopago_service.py — Servicio de integración con Mercado Pago Checkout Pro.

Encapsula toda la comunicación con la API de Mercado Pago en tres operaciones:
1. Crear una preferencia de pago (genera la URL a la que se redirige al usuario).
2. Verificar el estado real de un pago por payment_id.
3. Buscar pagos asociados a una preferencia (para cuando no tenemos payment_id).

Documentación oficial:
https://www.mercadopago.com.ar/developers/es/docs/checkout-pro/landing
"""

import mercadopago
from django.conf import settings


class ServicioMercadoPago:
    """
    Clase de servicio para interactuar con la API de Mercado Pago.
    Usa el SDK oficial de Python (pip install mercadopago).
    """

    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def crear_preferencia(self, funcion, cantidad_asientos, monto_total, external_reference, request):
        """
        Crea una preferencia de pago en Mercado Pago.

        Args:
            funcion: Instancia del modelo Funcion.
            cantidad_asientos: Número de entradas.
            monto_total: Decimal con el monto total.
            external_reference: Referencia única para vincular el pago con nuestra sesión.
            request: HttpRequest de Django.

        Returns:
            dict con 'preference_id' e 'init_point'
        """
        preference_data = {
            "items": [
                {
                    "title": f"CineFSA — {funcion.pelicula.titulo}",
                    "description": (
                        f"{cantidad_asientos} entrada(s) · "
                        f"{funcion.sala.nombre_sala} · "
                        f"{funcion.fecha:%d/%m/%Y} {funcion.hora_inicio:%H:%M}"
                    ),
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(monto_total),
                }
            ],
            # external_reference: Nuestro identificador único que MP devuelve en el pago.
            # Lo usamos para buscar el pago desde nuestro servidor sin depender de back_urls.
            "external_reference": external_reference,
        }

        result = self.sdk.preference().create(preference_data)

        # Verificar que la API respondió correctamente
        if result["status"] not in (200, 201):
            error_msg = "Error desconocido de Mercado Pago"
            if isinstance(result.get("response"), dict):
                error_msg = result["response"].get("message", error_msg)
            raise Exception(f"Mercado Pago rechazó la solicitud: {error_msg}")

        response = result["response"]

        return {
            "preference_id": response["id"],
            # sandbox_init_point: URL de pago para entorno de pruebas.
            # En producción se usaría "init_point" (sin sandbox).
            "init_point": response.get("sandbox_init_point", response.get("init_point")),
        }

    def verificar_pago(self, payment_id):
        """
        Consulta el estado REAL de un pago a la API de Mercado Pago por payment_id.
        """
        try:
            result = self.sdk.payment().get(int(payment_id))

            if result["status"] == 200:
                payment = result["response"]
                return {
                    "status": payment["status"],
                    "status_detail": payment.get("status_detail", ""),
                    "monto": payment.get("transaction_amount", 0),
                }

            return {
                "status": "error",
                "status_detail": f"API respondió con status HTTP {result['status']}",
                "monto": 0,
            }

        except Exception as e:
            return {
                "status": "error",
                "status_detail": str(e),
                "monto": 0,
            }

    def buscar_pago_por_referencia(self, external_reference):
        """
        Busca pagos asociados a un external_reference.
        
        Esto permite verificar el pago sin depender de back_urls ni webhooks.
        El usuario paga en otra pestaña y cuando vuelve, buscamos el pago
        en la API de MP usando la referencia que guardamos en la sesión.

        Args:
            external_reference: La referencia única que asignamos al crear la preferencia.

        Returns:
            dict con 'status', 'status_detail', 'payment_id', 'monto'
            o None si no se encontró ningún pago.
        """
        try:
            filters = {
                "external_reference": external_reference,
                "sort": "date_created",
                "criteria": "desc",
            }
            result = self.sdk.payment().search(filters)

            if result["status"] == 200:
                results = result["response"].get("results", [])
                if results:
                    # Tomar el pago más reciente
                    pago = results[0]
                    return {
                        "status": pago["status"],
                        "status_detail": pago.get("status_detail", ""),
                        "payment_id": pago["id"],
                        "monto": pago.get("transaction_amount", 0),
                    }

            return None

        except Exception as e:
            return None
