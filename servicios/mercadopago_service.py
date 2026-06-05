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
import requests as http_requests
from django.conf import settings


class ServicioMercadoPago:
    """
    Clase de servicio para interactuar con la API de Mercado Pago.
    Usa el SDK oficial de Python (pip install mercadopago).
    """

    def __init__(self):
        self.token = settings.MERCADOPAGO_ACCESS_TOKEN
        self.sdk = mercadopago.SDK(self.token)

    def crear_preferencia(self, funcion, cantidad_asientos, monto_total, external_reference, request):
        """
        Crea una preferencia de pago en Mercado Pago.
        Usa requests directamente para evitar bloqueos del PolicyAgent con el SDK.
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
            "external_reference": external_reference,
        }

        # Intentar primero con requests directo (evita bloqueo de PolicyAgent)
        print(f"[MP DEBUG] Enviando: {preference_data}")
        try:
            resp = http_requests.post(
                "https://api.mercadopago.com/checkout/preferences",
                json=preference_data,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            print(f"[MP DEBUG] HTTP directo - Status: {resp.status_code}")
            print(f"[MP DEBUG] HTTP directo - Response: {resp.text[:300]}")

            if resp.status_code in (200, 201):
                response = resp.json()
                return {
                    "preference_id": response["id"],
                    "init_point": response.get("sandbox_init_point", response.get("init_point")),
                }
        except Exception as e:
            print(f"[MP DEBUG] HTTP directo falló: {e}")

        # Fallback al SDK
        result = self.sdk.preference().create(preference_data)

        if result["status"] not in (200, 201):
            error_msg = "Error desconocido de Mercado Pago"
            if isinstance(result.get("response"), dict):
                error_msg = result["response"].get("message", error_msg)
            raise Exception(f"Mercado Pago rechazó la solicitud: {error_msg}")

        response = result["response"]

        return {
            "preference_id": response["id"],
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
