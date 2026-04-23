"""
genero.py — Modelo para los géneros cinematográficos.

Representa las categorías temáticas de las películas (Acción, Comedia, Terror, etc.).
Una película puede pertenecer a múltiples géneros simultáneamente (relación M:N),
lo que permite una clasificación flexible y facilita los filtros de búsqueda
en el portal del cliente sin duplicar información del filme.
"""

from django.db import models


class Genero(models.Model):
    """
    Entidad: genero
    Almacena los géneros cinematográficos disponibles en el sistema.
    Se vincula con Pelicula mediante una relación muchos a muchos definida en el modelo Pelicula.
    """

    # ─── CAMPOS ───────────────────────────────────────────────────────────────

    # descripcion: Nombre del género cinematográfico.
    # Ejemplo: 'Acción', 'Comedia', 'Ciencia Ficción', 'Terror'.
    # Se marca como unique para evitar géneros duplicados en la base de datos.
    descripcion = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Descripción'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        # app_label: Indica a Django que este modelo pertenece a la app 'sistema_cine',
        # aunque el archivo esté físicamente en 'modelos/' y no dentro de 'sistema_cine/'.
        app_label = 'sistema_cine'

        # db_table: Nombre explícito de la tabla en MySQL.
        # Si no se define, Django genera uno automático (ej: 'sistema_cine_genero').
        db_table = 'genero'

        # verbose_name: Nombre legible en singular para el panel de administración.
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'

        # ordering: Orden por defecto en las consultas (alfabético por descripción).
        ordering = ['descripcion']

    def __str__(self):
        """Representación en texto del género (se muestra en el admin y en selects)."""
        return self.descripcion
