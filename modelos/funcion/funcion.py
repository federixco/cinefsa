"""
funcion.py — Modelo para las funciones (proyecciones programadas).

Representa un evento de proyección específico: la combinación de una película,
una sala, una fecha, un horario y un precio. Es el eje temporal del sistema
que cruza la infraestructura (Sala) con el contenido (Pelicula) en un marco
de tiempo determinado. Cada función emite un número de tickets limitado por
la capacidad de la sala asignada.
"""

from django.db import models


class Funcion(models.Model):
    """
    Entidad: funcion
    Modela cada sesión de proyección en el complejo. Implementa dos relaciones:
    - PROYECTADA_EN: Pelicula (1) → Funcion (N) — una película se exhibe en múltiples horarios.
    - ALBERGA: Sala (1) → Funcion (N) — una sala aloja múltiples funciones en distintos momentos.
    """

    # ─── CLAVES FORÁNEAS ──────────────────────────────────────────────────────

    # pelicula: FK que implementa la relación PROYECTADA_EN.
    # on_delete=CASCADE: si se elimina una película del sistema,
    # se eliminan todas sus funciones programadas (ya no hay contenido que proyectar).
    # related_name='funciones': permite acceder desde una película a sus funciones
    # con pelicula.funciones.all()
    pelicula = models.ForeignKey(
        'Pelicula',
        on_delete=models.CASCADE,
        related_name='funciones',
        verbose_name='Película'
    )

    # sala: FK que implementa la relación ALBERGA.
    # on_delete=CASCADE: si se elimina una sala, se eliminan sus funciones
    # (no se puede proyectar en un espacio que ya no existe).
    # related_name='funciones': permite acceder desde una sala a sus funciones
    # con sala.funciones.all()
    sala = models.ForeignKey(
        'Sala',
        on_delete=models.CASCADE,
        related_name='funciones',
        verbose_name='Sala'
    )

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # fecha: Día en que se realiza la proyección.
    # Se almacena como DATE en MySQL (sin hora). Ejemplo: 2026-05-15.
    fecha = models.DateField(
        verbose_name='Fecha'
    )

    # hora_inicio: Hora de comienzo de la función.
    # Se almacena como TIME en MySQL. Ejemplo: 20:30:00.
    # Separar fecha y hora permite consultas eficientes por día (cartelera diaria)
    # y por franja horaria (funciones de la tarde, noche, etc.).
    hora_inicio = models.TimeField(
        verbose_name='Hora de inicio'
    )

    # precio_entrada: Valor monetario del ticket para esta función.
    # DecimalField con max_digits=8 y decimal_places=2 permite valores
    # de hasta $999.999,99 (suficiente para precios en pesos argentinos).
    # Cada función puede tener un precio distinto (matinée, trasnoche, 3D, etc.).
    precio_entrada = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Precio de entrada'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'funcion'
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'

        # ordering: Ordenar por fecha y hora (las funciones más próximas primero).
        ordering = ['fecha', 'hora_inicio']

        # unique_together: Restricción de unicidad compuesta.
        # Impide que se programen dos funciones en la misma sala, el mismo día y a la misma hora.
        # Es el mecanismo que previene la superposición de proyecciones en un espacio físico.
        unique_together = ['sala', 'fecha', 'hora_inicio']

    def __str__(self):
        """Representación: 'Película - Sala (DD/MM/YYYY HH:MM)'."""
        return f'{self.pelicula.titulo} - {self.sala.nombre_sala} ({self.fecha:%d/%m/%Y} {self.hora_inicio:%H:%M})'
