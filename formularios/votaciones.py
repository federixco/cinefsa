"""
votaciones.py — Formulario de encuestas de votación (RF-A04).

Formularios:
    - FormularioEncuesta: ModelForm para crear y editar encuestas de votación
      del Cine Club, con validación de fechas y filtro de películas clásicas.
"""

from django import forms

from sistema_cine.models import Encuesta, Pelicula


class FormularioEncuesta(forms.ModelForm):
    """
    ModelForm para crear y editar encuestas de votación del Cine Club (RF-A04).

    El campo 'peliculas' filtra el queryset para mostrar únicamente
    aquellas películas marcadas como clásicas en la gestión de cartelera.
    """

    class Meta:
        model = Encuesta
        fields = [
            'titulo',
            'descripcion',
            'fecha_evento',
            'fecha_inicio',
            'fecha_fin',
            'peliculas',
            'esta_activa',
        ]
        labels = {
            'titulo':       'Título de la encuesta',
            'descripcion':  'Descripción del evento (opcional)',
            'fecha_evento': 'Fecha del evento especial',
            'fecha_inicio': 'Inicio de la votación',
            'fecha_fin':    'Cierre de la votación',
            'peliculas':    'Películas candidatas (solo clásicas)',
            'esta_activa':  '¿Activar encuesta al guardar?',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={
                'id':          'campo-encuesta-titulo',
                'placeholder': 'Ej: Cine Club — Noche de Clásicos Julio 2026',
            }),
            'descripcion': forms.Textarea(attrs={
                'id':          'campo-encuesta-descripcion',
                'rows':        3,
                'placeholder': 'Describí el evento especial para los clientes...',
            }),
            'fecha_evento': forms.DateInput(
                attrs={'id': 'campo-encuesta-fecha-evento', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'id': 'campo-encuesta-fecha-inicio', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'id': 'campo-encuesta-fecha-fin', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'peliculas': forms.CheckboxSelectMultiple(attrs={
                'id': 'campo-encuesta-peliculas',
            }),
            'esta_activa': forms.CheckboxInput(attrs={
                'id': 'campo-encuesta-activa',
            }),
        }
        error_messages = {
            'titulo':       {'required': 'El título de la encuesta es obligatorio.'},
            'fecha_evento': {'required': 'Ingresá la fecha del evento especial.'},
            'fecha_inicio': {'required': 'Ingresá la fecha y hora de inicio de la votación.'},
            'fecha_fin':    {'required': 'Ingresá la fecha y hora de cierre de la votación.'},
        }

    def __init__(self, *args, **kwargs):
        """Filtra el queryset de películas para mostrar solo las clásicas."""
        super().__init__(*args, **kwargs)
        self.fields['peliculas'].queryset = Pelicula.objects.filter(
            es_clasica=True
        ).order_by('titulo')

    def clean(self):
        """
        Validación de fechas:
        - fecha_fin debe ser posterior a fecha_inicio.
        - fecha_inicio no puede ser posterior a fecha_evento.
        - fecha_fin no puede ser posterior a fecha_evento.
        """
        datos = super().clean()
        fecha_inicio = datos.get('fecha_inicio')
        fecha_fin    = datos.get('fecha_fin')
        fecha_evento = datos.get('fecha_evento')

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                self.add_error(
                    'fecha_fin',
                    'La fecha de cierre debe ser posterior a la fecha de inicio.'
                )

        if fecha_evento:
            if fecha_inicio and fecha_inicio.date() > fecha_evento:
                self.add_error(
                    'fecha_inicio',
                    'La votación no puede iniciar después del día del evento.'
                )
            if fecha_fin and fecha_fin.date() > fecha_evento:
                self.add_error(
                    'fecha_fin',
                    'La votación no puede finalizar después del día del evento.'
                )

        return datos
