"""
cartelera.py — Formularios de gestión de cartelera (RF-A02).

Formularios:
    - FormularioGenero:   ModelForm para crear/editar géneros cinematográficos.
    - FormularioPelicula: ModelForm para crear/editar películas (géneros M2M + póster).
    - FormularioFuncion:  ModelForm para programar funciones con validación de
                          superposición horaria en la misma sala y día.
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from sistema_cine.models import Genero, Pelicula, Funcion, Sala


class FormularioGenero(forms.ModelForm):
    """
    ModelForm para crear y editar géneros cinematográficos (RF-A02).

    Aprovecha la validación automática de unicidad que Django hereda del
    campo unique=True del modelo Genero.
    """

    class Meta:
        model = Genero
        fields = ['descripcion']
        labels = {
            'descripcion': 'Nombre del género',
        }
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'id':          'campo-genero-descripcion',
                'placeholder': 'Ej: Acción, Comedia, Terror...',
                'autocomplete':'off',
                'maxlength':   '100',
                'class':       'modal-input',
            }),
        }
        error_messages = {
            'descripcion': {
                'unique':     'Ya existe un género con ese nombre.',
                'required':   'El nombre del género es obligatorio.',
                'max_length': 'El nombre del género no puede tener más de 100 caracteres.',
            },
        }


class FormularioPelicula(forms.ModelForm):
    """
    ModelForm para crear y editar películas (RF-A02).

    IMPORTANTE: La plantilla debe incluir enctype="multipart/form-data"
    para que Django procese correctamente el campo imagen_poster.
    """

    class Meta:
        model = Pelicula
        fields = [
            'titulo',
            'sinopsis',
            'duracion_minutos',
            'clasificacion',
            'estado',
            'generos',
            'es_clasica',
            'imagen_poster',
        ]
        labels = {
            'titulo':           'Título',
            'sinopsis':         'Sinopsis',
            'duracion_minutos': 'Duración (minutos)',
            'clasificacion':    'Clasificación etaria',
            'estado':           'Estado en cartelera',
            'generos':          'Géneros',
            'es_clasica':       '¿Es película clásica?',
            'imagen_poster':    'Póster de la película',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={
                'id':          'campo-pelicula-titulo',
                'placeholder': 'Ej: El Señor de los Anillos',
                'maxlength':   '200',
            }),
            'sinopsis': forms.Textarea(attrs={
                'id':          'campo-pelicula-sinopsis',
                'rows':        4,
                'placeholder': 'Escribí la sinopsis de la película...',
            }),
            'duracion_minutos': forms.NumberInput(attrs={
                'id':          'campo-pelicula-duracion',
                'min':         '1',
                'placeholder': 'Ej: 148',
            }),
            'clasificacion': forms.Select(attrs={
                'id': 'campo-pelicula-clasificacion',
            }),
            'generos': forms.CheckboxSelectMultiple(attrs={
                'id': 'campo-pelicula-generos',
            }),
            'es_clasica': forms.CheckboxInput(attrs={
                'id': 'campo-pelicula-es-clasica',
            }),
            'estado': forms.Select(attrs={
                'id': 'campo-pelicula-estado',
            }),
            'imagen_poster': forms.ClearableFileInput(attrs={
                'id':     'campo-pelicula-poster',
                'accept': 'image/*',
            }),
        }
        error_messages = {
            'titulo': {
                'required':   'El título de la película es obligatorio.',
                'max_length': 'El título no puede superar los 200 caracteres.',
            },
            'sinopsis': {
                'required': 'La sinopsis es obligatoria.',
            },
            'duracion_minutos': {
                'required':  'La duración es obligatoria.',
                'invalid':   'Ingresá un número entero válido para la duración.',
                'min_value': 'La duración debe ser mayor a 0 minutos.',
            },
            'clasificacion': {
                'required': 'Seleccioná una clasificación etaria.',
            },
        }

    def clean_duracion_minutos(self):
        """Validación personalizada: la duración debe ser mayor a 0."""
        duracion = self.cleaned_data.get('duracion_minutos')

        if duracion is not None and duracion <= 0:
            raise ValidationError('La duración debe ser mayor a 0 minutos.')

        return duracion


class FormularioFuncion(forms.ModelForm):
    """
    ModelForm para programar funciones (proyecciones) en una sala (RF-A02).

    Validación de superposición horaria (método clean()):
        Verifica que el rango temporal de la nueva función no se solape
        con ninguna función ya existente en la misma sala y fecha.
    """

    class Meta:
        model = Funcion
        fields = [
            'pelicula',
            'sala',
            'fecha',
            'hora_inicio',
            'precio_entrada',
        ]
        labels = {
            'pelicula':       'Película',
            'sala':           'Sala',
            'fecha':          'Fecha de la función',
            'hora_inicio':    'Hora de inicio',
            'precio_entrada': 'Precio de entrada ($)',
        }
        widgets = {
            'pelicula': forms.Select(attrs={
                'id': 'campo-funcion-pelicula',
            }),
            'sala': forms.Select(attrs={
                'id': 'campo-funcion-sala',
            }),
            'fecha': forms.DateInput(
                attrs={
                    'id':   'campo-funcion-fecha',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            'hora_inicio': forms.TimeInput(
                attrs={
                    'id':   'campo-funcion-hora-inicio',
                    'type': 'time',
                },
                format='%H:%M',
            ),
            'precio_entrada': forms.NumberInput(attrs={
                'id':          'campo-funcion-precio',
                'min':         '0',
                'step':        '0.01',
                'placeholder': 'Ej: 3500.00',
            }),
        }
        error_messages = {
            'pelicula':  { 'required': 'Seleccioná una película.' },
            'sala':      { 'required': 'Seleccioná una sala.' },
            'fecha':     { 'required': 'Ingresá la fecha de la función.', 'invalid': 'Ingresá una fecha válida.' },
            'hora_inicio': { 'required': 'Ingresá la hora de inicio.', 'invalid': 'Ingresá una hora válida.' },
            'precio_entrada': { 'required': 'Ingresá el precio de la entrada.', 'invalid': 'Ingresá un precio válido (ej: 3500.00).' },
        }

    def __init__(self, *args, **kwargs):
        """Solo muestra salas con estado 'activa' en el select y oculta películas retiradas."""
        super().__init__(*args, **kwargs)
        self.fields['sala'].queryset     = Sala.objects.filter(estado='activa')
        self.fields['pelicula'].queryset = Pelicula.objects.exclude(estado='retirada')
        self.fields['pelicula'].empty_label = '--- Seleccioná una película ---'
        self.fields['sala'].empty_label     = '--- Seleccioná una sala ---'

    def clean(self):
        """
        Validaciones:
        1. FECHA NO PASADA.
        2. HORA NO PASADA (si la fecha es hoy).
        3. SUPERPOSICIÓN HORARIA en la misma sala y día.
        """
        from django.utils import timezone

        datos = super().clean()

        sala        = datos.get('sala')
        fecha       = datos.get('fecha')
        hora_inicio = datos.get('hora_inicio')
        pelicula    = datos.get('pelicula')

        # ── Validación 1: No se permiten fechas pasadas ──────────────────────────
        if fecha:
            hoy = timezone.localdate()
            if fecha < hoy:
                self.add_error(
                    'fecha',
                    'No pods programar funciones en fechas que ya pasaron.'
                )

        # ── Validación 2: Si es hoy, la hora debe ser futura ────────────────────
        if fecha and hora_inicio:
            hoy = timezone.localdate()
            if fecha == hoy:
                hora_actual = timezone.localtime(timezone.now()).time()
                if hora_inicio <= hora_actual:
                    self.add_error(
                        'hora_inicio',
                        f'La función es para hoy. La hora de inicio debe ser posterior '
                        f'a la hora actual ({hora_actual:%H:%M}).'
                    )

        # ── Validación 3: Superposición horaria ─────────────────────────────────
        if sala and fecha and hora_inicio and pelicula:
            inicio_dt = datetime.combine(fecha, hora_inicio)
            fin_dt    = inicio_dt + timedelta(minutes=pelicula.duracion_minutos)
            hora_fin  = fin_dt.time()

            funciones_existentes = Funcion.objects.filter(sala=sala, fecha=fecha)

            if self.instance and self.instance.pk:
                funciones_existentes = funciones_existentes.exclude(pk=self.instance.pk)

            for funcion_existente in funciones_existentes:
                inicio_exist_dt = datetime.combine(fecha, funcion_existente.hora_inicio)
                fin_exist_dt    = inicio_exist_dt + timedelta(
                    minutes=funcion_existente.pelicula.duracion_minutos
                )
                hora_fin_exist = fin_exist_dt.time()

                hay_superposicion = (hora_inicio < hora_fin_exist) and (hora_fin > funcion_existente.hora_inicio)

                if hay_superposicion:
                    raise ValidationError(
                        f'Conflicto de horario: la sala "{sala.nombre_sala}" ya tiene '
                        f'"{funcion_existente.pelicula.titulo}" de '
                        f'{funcion_existente.hora_inicio:%H:%M} a {hora_fin_exist:%H:%M}. '
                        f'La nueva función duraría hasta las {hora_fin:%H:%M}.'
                    )

        return datos
