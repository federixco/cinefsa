"""
qr_service.py — Servicio de generación de códigos QR para tickets.

Genera imágenes QR con el código único de cada ticket y las guarda
en el campo imagen_qr del modelo Ticket (FileField → multimedia/tickets_qr/).
"""

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


def generar_qr_ticket(ticket):
    """
    Genera una imagen QR para un ticket y la guarda en su campo imagen_qr.

    El contenido del QR sigue el formato: CINEFSA-TICKET-{uuid}
    que es leído por el validador QR del empleado (vistas/validador_qr.py).

    Args:
        ticket: instancia del modelo Ticket con codigo_qr ya asignado.
    """
    contenido_qr = f"CINEFSA-TICKET-{ticket.codigo_qr}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(contenido_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    nombre_archivo = f"ticket_{ticket.id_ticket}_{ticket.codigo_qr}.png"
    ticket.imagen_qr.save(nombre_archivo, ContentFile(buffer.read()), save=True)
