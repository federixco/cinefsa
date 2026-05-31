"""
votacion.py — Modelos del módulo de Cine Club / Votación (RF-C04 y RF-A04).

Define las dos entidades centrales del sistema de votación:

    - Encuesta: Representa una convocatoria de votación creada por el
      administrador. Contiene el título, descripción, la fecha del evento
      especial a programar, el rango de fechas en que se puede votar
      y las películas clásicas candidatas.

    - Voto: Registro atómico de un voto emitido por un cliente autenticado
      en una encuesta determinada. La restricción unique_together garantiza
      que cada cliente solo pueda votar una vez por encuesta.

Relaciones:
    Encuesta  ──(M:N)──  Pelicula   (peliculas candidatas, solo las clásicas)
    Encuesta  ──(1:N)──  Voto
    Cliente   ──(1:N)──  Voto
    Pelicula  ──(1:N)──  Voto
"""

from django.db import models
from django.utils import timezone


class Encuesta(models.Model):
    """
    Entidad: encuesta

    Modela una convocatoria de votación abierta por el administrador para que
    los clientes registrados voten cuál película clásica desean ver proyectada
    en una fecha especial de tipo 'Cine Club'.

    Tabla en MySQL: 'encuesta'
    """

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # titulo: Nombre descriptivo de la encuesta que se muestra en el portal.
    # Ej: "Cine Club — Noche de Clásicos, Julio 2026"
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la encuesta'
    )

    # descripcion: Texto explicativo para el cliente sobre el evento especial.
    descripcion = models.TextField(
        verbose_name='Descripción',
        blank=True,
        default=''
    )

    # fecha_evento: La fecha del evento especial que se está programando.
    # No es la fecha de votación, sino el día del evento en el cine.
    fecha_evento = models.DateField(
        verbose_name='Fecha del evento especial'
    )

    # fecha_inicio: Desde cuándo los clientes pueden votar (inclusive).
    fecha_inicio = models.DateTimeField(
        verbose_name='Inicio de la votación'
    )

    # fecha_fin: Hasta cuándo los clientes pueden votar (inclusive).
    fecha_fin = models.DateTimeField(
        verbose_name='Cierre de la votación'
    )

    # peliculas: Películas candidatas para esta encuesta.
    # Solo deberían incluirse películas con es_clasica=True (validado en el formulario).
    # ManyToMany: una encuesta tiene varias películas candidatas,
    # y una película puede participar en varias encuestas distintas.
    peliculas = models.ManyToManyField(
        'Pelicula',
        related_name='encuestas',
        verbose_name='Películas candidatas',
        limit_choices_to={'es_clasica': True}
    )

    # esta_activa: Control manual del administrador para abrir/cerrar la encuesta.
    # Una encuesta puede estar dentro del rango de fechas y aun así estar
    # desactivada manualmente por el admin.
    esta_activa = models.BooleanField(
        default=True,
        verbose_name='¿Está activa?'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'encuesta'
        verbose_name = 'Encuesta de votación'
        verbose_name_plural = 'Encuestas de votación'
        # Las encuestas más recientes primero
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.titulo} (Evento: {self.fecha_evento:%d/%m/%Y})'

    # ─── MÉTODOS DE NEGOCIO ────────────────────────────────────────────────────

    def esta_en_periodo(self):
        """
        Retorna True si la fecha y hora actual están dentro del rango de
        votación (fecha_inicio <= ahora <= fecha_fin).
        """
        ahora = timezone.now()
        return self.fecha_inicio <= ahora <= self.fecha_fin

    def esta_disponible(self):
        """
        Retorna True si la encuesta está activa Y dentro del período de votación.
        Este es el método principal que determina si un cliente puede votar.
        """
        return self.esta_activa and self.esta_en_periodo()

    def total_votos(self):
        """Retorna el total de votos emitidos en esta encuesta."""
        return self.votos.count()

    def resultados(self):
        """
        Retorna una lista de diccionarios con los resultados por película,
        ordenados de mayor a menor cantidad de votos.

        Estructura de cada ítem:
            {
                'pelicula': <Pelicula>,
                'cantidad': int,
                'porcentaje': float (0-100),
            }
        """
        total = self.total_votos()
        items = []

        for pelicula in self.peliculas.all():
            cantidad = self.votos.filter(pelicula=pelicula).count()
            porcentaje = round((cantidad / total * 100), 1) if total > 0 else 0
            items.append({
                'pelicula': pelicula,
                'cantidad': cantidad,
                'porcentaje': porcentaje,
            })

        # Ordenar de mayor a menor votos
        return sorted(items, key=lambda x: x['cantidad'], reverse=True)


class Voto(models.Model):
    """
    Entidad: voto

    Registro de un voto individual emitido por un cliente en una encuesta.
    La restricción unique_together ('cliente', 'encuesta') garantiza a nivel
    de base de datos que cada cliente solo pueda votar una vez por encuesta.

    Tabla en MySQL: 'voto'
    """

    # ─── CLAVES FORÁNEAS ──────────────────────────────────────────────────────

    # cliente: El cliente que emitió el voto.
    # on_delete=CASCADE: si se elimina el cliente, se elimina su voto.
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='votos',
        verbose_name='Cliente'
    )

    # encuesta: La encuesta en la que se emitió el voto.
    # related_name='votos': permite acceder con encuesta.votos.all()
    encuesta = models.ForeignKey(
        Encuesta,
        on_delete=models.CASCADE,
        related_name='votos',
        verbose_name='Encuesta'
    )

    # pelicula: La película por la que votó el cliente.
    pelicula = models.ForeignKey(
        'Pelicula',
        on_delete=models.CASCADE,
        related_name='votos_recibidos',
        verbose_name='Película votada'
    )

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # fecha_voto: Timestamp automático del momento en que se registró el voto.
    # auto_now_add=True: Django lo completa solo al hacer el INSERT.
    fecha_voto = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora del voto'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'voto'
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'

        # RESTRICCIÓN CRÍTICA: Un cliente solo puede votar UNA VEZ por encuesta.
        # Esta restricción se aplica a nivel de base de datos (UNIQUE KEY en MySQL).
        unique_together = [['cliente', 'encuesta']]

        ordering = ['-fecha_voto']

    def __str__(self):
        return (
            f'{self.cliente.usuario_id_usuario.nombre_completo} votó por '
            f'"{self.pelicula.titulo}" en "{self.encuesta.titulo}"'
        )
