"""
pelicula.py — Modelo para las películas del complejo cinematográfico.

Representa la información fija de cada filme: título, sinopsis, duración, clasificación
etaria, póster y si es considerada clásica (apta para el módulo de votación Cine Club).
Se vincula con Genero mediante una relación muchos a muchos (una película puede tener
múltiples géneros: ej. Acción + Ciencia Ficción).
"""

from django.db import models


class Pelicula(models.Model):
    """
    Entidad: pelicula
    Almacena los datos descriptivos e inmutables de cada filme.
    Es el eje de contenido del sistema: se conecta con Funcion (programación)
    y con Genero (clasificación temática).
    """

    # ─── CHOICES (Valores restringidos) ───────────────────────────────────────

    # CLASIFICACION_CHOICES: Restricción de edad según normativa argentina.
    # Se implementa como choices de Django, que genera un ENUM lógico a nivel aplicación
    # y valida que solo se ingresen estos valores en formularios y serializadores.
    CLASIFICACION_CHOICES = [
        ('ATP', 'Apta para Todo Público'),
        ('+13', 'Mayores de 13 años'),
        ('+16', 'Mayores de 16 años'),
        ('+18', 'Mayores de 18 años'),
    ]

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # titulo: Nombre comercial de la película.
    # max_length=200 cubre títulos largos (ej: "El Señor de los Anillos: El Retorno del Rey").
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )

    # sinopsis: Resumen argumental del filme para mostrar en la cartelera del portal.
    # Se usa TextField (TEXT en MySQL) porque las sinopsis pueden ser extensas.
    sinopsis = models.TextField(
        verbose_name='Sinopsis'
    )

    # duracion_minutos: Longitud temporal del filme en minutos.
    # PositiveIntegerField garantiza que no se ingresen valores negativos.
    # Ejemplo: 148 (para una película de 2h 28min).
    duracion_minutos = models.PositiveIntegerField(
        verbose_name='Duración (minutos)'
    )

    # clasificacion: Restricción etaria del filme.
    # Usa las choices definidas arriba para validar los valores permitidos.
    # max_length=3 cubre el valor más largo ('+18' = 3 caracteres).
    clasificacion = models.CharField(
        max_length=3,
        choices=CLASIFICACION_CHOICES,
        verbose_name='Clasificación'
    )

    # generos: Relación ManyToMany con la entidad Genero.
    # Django crea automáticamente una tabla intermedia (pelicula_generos)
    # que almacena pares (id_pelicula, id_genero).
    # Esto implementa la relación PERTENECE del modelo conceptual (M:N).
    generos = models.ManyToManyField(
        'Genero',
        related_name='peliculas',
        verbose_name='Géneros'
    )

    # es_clasica: Indicador booleano que marca si la película es considerada "clásica".
    # Las películas clásicas son las que aparecen en el módulo de votación Cine Club
    # para que los usuarios voten cuáles proyectar en fechas especiales.
    # default=False: por defecto, una película nueva no es clásica.
    es_clasica = models.BooleanField(
        default=False,
        verbose_name='¿Es clásica?'
    )

    # imagen_poster: Ruta al archivo de imagen del póster de la película.
    # Se sube a la carpeta /multimedia/posters/ del servidor.
    # ImageField requiere Pillow instalado (ya incluido en las dependencias).
    # blank=True / null=True: el póster es opcional al momento de cargar la película.
    imagen_poster = models.ImageField(
        upload_to='posters/',
        blank=True,
        null=True,
        verbose_name='Póster'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'pelicula'
        verbose_name = 'Película'
        verbose_name_plural = 'Películas'

        # ordering: Orden alfabético por título como criterio por defecto.
        ordering = ['titulo']

    def __str__(self):
        """Representación en texto: 'Título (Clasificación)'."""
        return f'{self.titulo} ({self.clasificacion})'
