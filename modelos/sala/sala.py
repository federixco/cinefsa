"""
sala.py — Modelo para las salas del complejo cinematográfico.

Representa el espacio físico donde se proyectan las funciones.
Cada sala tiene un nombre identificatorio, una capacidad máxima de butacas,
un estado operativo (activa o en mantenimiento) y un campo JSON que almacena
la configuración del layout diseñado con el Editor Dinámico (RF-A01).
"""

from django.db import models


class Sala(models.Model):
    """
    Entidad: sala
    Modela la infraestructura física del complejo. Cada sala CONTIENE múltiples
    asientos (relación 1:N definida en el modelo Asiento) y ALBERGA múltiples
    funciones a lo largo del tiempo (relación 1:N definida en el modelo Funcion).
    """

    # ─── CHOICES ──────────────────────────────────────────────────────────────

    # ESTADO_CHOICES: Estado operativo de la sala.
    # 'activa': la sala está disponible para programar funciones.
    # 'mantenimiento': la sala está temporalmente fuera de servicio.
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('mantenimiento', 'En mantenimiento'),
    ]

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # nombre_sala: Identificador legible de la sala.
    # Ejemplo: 'Sala 1', 'Sala VIP', 'Sala IMAX'.
    # unique=True evita nombres duplicados que confundan al administrador.
    nombre_sala = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la sala'
    )

    # capacidad_maxima: Cantidad total de butacas disponibles en la sala.
    # Este valor se usa como tope para la generación de asientos en el editor
    # y para controlar la venta de entradas (no se pueden vender más tickets
    # que butacas disponibles para una función en esta sala).
    capacidad_maxima = models.PositiveIntegerField(
        verbose_name='Capacidad máxima'
    )

    # layout_config: Configuración del mapa de butacas en formato JSON.
    # Almacena la distribución espacial diseñada desde el Editor Dinámico (RF-A01):
    # filas, columnas, pasillos, zonas VIP, etc.
    # JSONField se mapea a un campo JSON nativo en MySQL 5.7+.
    # blank=True / null=True: puede estar vacío antes de diseñar el layout.
    layout_config = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Configuración del layout'
    )

    # estado: Estado operativo actual de la sala.
    # default='activa': una sala recién creada se asume operativa.
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='activa',
        verbose_name='Estado'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'sala'
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['nombre_sala']

    def __str__(self):
        """Representación en texto: 'Nombre (estado)'."""
        return f'{self.nombre_sala} ({self.get_estado_display()})'
