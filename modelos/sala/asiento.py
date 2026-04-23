"""
asiento.py — Modelo para las butacas individuales de cada sala.

Representa cada lugar físico dentro de una sala. Cada asiento tiene una ubicación
lógica (fila y número) y coordenadas espaciales (posicion_x, posicion_y) que
permiten renderizar el mapa interactivo de selección de butacas en el portal del
cliente y en el Editor Dinámico del administrador (RF-A01).
"""

from django.db import models


class Asiento(models.Model):
    """
    Entidad: asiento
    Modela una butaca individual dentro de una sala. La relación CONTIENE (Sala 1 → N Asiento)
    se implementa mediante la FK 'sala'. Las coordenadas X/Y permiten construir la matriz
    visual del mapa de butacas para la compra online y la venta presencial.
    """

    # ─── CHOICES ──────────────────────────────────────────────────────────────

    # TIPO_CHOICES: Categoría de la butaca según su ubicación o características.
    # 'general': asiento estándar.
    # 'vip': asiento premium (mejor ubicación, posible recargo).
    # 'discapacitado': asiento adaptado para personas con movilidad reducida.
    TIPO_CHOICES = [
        ('general', 'General'),
        ('vip', 'VIP'),
        ('discapacitado', 'Discapacitado'),
    ]

    # ─── CLAVES FORÁNEAS ──────────────────────────────────────────────────────

    # sala: FK que implementa la relación CONTIENE (Sala 1 → N Asiento).
    # on_delete=CASCADE: si se elimina una sala, se eliminan todos sus asientos
    # (la infraestructura física deja de existir, los asientos no tienen sentido solos).
    # related_name='asientos': permite acceder desde una sala a sus butacas con sala.asientos.all()
    sala = models.ForeignKey(
        'Sala',
        on_delete=models.CASCADE,
        related_name='asientos',
        verbose_name='Sala'
    )

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # fila: Identificador de la fila dentro de la sala.
    # Ejemplo: 'A', 'B', 'C' o '1', '2', '3' (según convención del cine).
    fila = models.CharField(
        max_length=5,
        verbose_name='Fila'
    )

    # numero: Número de asiento dentro de la fila.
    # Ejemplo: en la fila 'A', los asientos van del 1 al 20.
    numero = models.PositiveIntegerField(
        verbose_name='Número'
    )

    # tipo_asiento: Categoría de la butaca (general, VIP o discapacitado).
    # default='general': la mayoría de los asientos son estándar.
    tipo_asiento = models.CharField(
        max_length=15,
        choices=TIPO_CHOICES,
        default='general',
        verbose_name='Tipo de asiento'
    )

    # posicion_x: Coordenada horizontal del asiento en la matriz visual del editor.
    # Junto con posicion_y, permite ubicar la butaca en el mapa interactivo 2D
    # que se renderiza en el frontend (tanto para el cliente como para el admin).
    posicion_x = models.PositiveIntegerField(
        verbose_name='Posición X'
    )

    # posicion_y: Coordenada vertical del asiento en la matriz visual del editor.
    posicion_y = models.PositiveIntegerField(
        verbose_name='Posición Y'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'asiento'
        verbose_name = 'Asiento'
        verbose_name_plural = 'Asientos'

        # ordering: Ordenar por fila y luego por número (A1, A2, ..., B1, B2, ...).
        ordering = ['sala', 'fila', 'numero']

        # unique_together: Restricción de unicidad compuesta.
        # Garantiza que no existan dos asientos con la misma fila y número en la misma sala.
        # Esto es el candado que impide butacas duplicadas en el mapa de la sala.
        unique_together = ['sala', 'fila', 'numero']

    def __str__(self):
        """Representación en texto: 'Sala X - Fila Y - Asiento Z'."""
        return f'{self.sala.nombre_sala} - Fila {self.fila} - Asiento {self.numero}'
