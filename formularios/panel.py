"""
panel.py — Formularios del panel de administración del sistema CineFSA.

Define los formularios usados en el panel interno de gestión,
accesible exclusivamente por el rol de Administrador.

Formularios RF-A05 (Gestión de Usuarios y Permisos):
    - FormularioBusquedaUsuario: Campo de texto para buscar usuarios
      registrados por nombre completo o dirección de email.
    - FormularioAsignarEmpleado: Campos necesarios para crear el registro
      en la tabla 'empleado': terminal_venta (id_validador se auto-genera).

Formularios RF-A02 (Gestión de Cartelera):
    - FormularioGenero:   ModelForm para crear/editar géneros cinematográficos.
    - FormularioPelicula: ModelForm para crear/editar películas (géneros M2M + póster).
    - FormularioFuncion:  ModelForm para programar funciones con validación de
                          superposición horaria en la misma sala y día.
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from sistema_cine.models import Genero, Pelicula, Funcion, Sala


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE BÚSQUEDA DE USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

class FormularioBusquedaUsuario(forms.Form):
    """
    Formulario de búsqueda de usuarios para el panel de gestión (RF-A05).

    Contiene un único campo de texto libre que se usa para filtrar usuarios
    por nombre completo o email. La búsqueda es parcial (icontains) y
    no distingue entre mayúsculas y minúsculas.

    Este formulario se envía por GET (no POST) para que el término de búsqueda
    quede en la URL y pueda ser compartido o recargado sin perder el resultado.
    """

    busqueda = forms.CharField(
        # El campo no es requerido: si está vacío, simplemente no se muestra ningún resultado
        required=False,
        label='Buscar usuario',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre completo o email del usuario...',
            # id personalizado para identificarlo en la plantilla sin ambigüedad
            'id': 'campo-busqueda-usuario',
            'autocomplete': 'off',
        }),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE ASIGNACIÓN DE ROL EMPLEADO
# ══════════════════════════════════════════════════════════════════════════════

class FormularioAsignarEmpleado(forms.Form):
    """
    Formulario para asignar el rol de Empleado a un usuario (RF-A05).

    Se muestra como un modal o sección expandible dentro del panel cuando
    el administrador hace clic en "Asignar como Empleado".

    Campos:
        - id_validador:   Código único del empleado para el sistema de validación QR.
                          Debe ser único en toda la tabla 'empleado' (validado en la BD).
        - terminal_venta: Número de la terminal/caja asignada al empleado (entero positivo).

    Estos datos son obligatorios según el modelo Empleado definido en
    modelos/identidad/usuario.py (ambos campos no tienen default).
    """

    id_validador = forms.CharField(
        max_length=50,
        label='ID de validador (QR)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: EMP-2026-001',
            'id': 'campo-id-validador',
        }),
        help_text=(
            'Código único que identifica al empleado en el sistema de '
            'validación de entradas QR en la puerta de acceso.'
        ),
    )

    terminal_venta = forms.IntegerField(
        min_value=1,  # No se permite 0 ni números negativos
        label='Número de terminal de venta',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ej: 3',
            'id': 'campo-terminal-venta',
            'min': '1',
        }),
        help_text=(
            'Número de caja o terminal asignada para emisión de boletos. '
            'Debe ser un número entero mayor a 0.'
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE GÉNERO CINEMATOGRÁFICO (RF-A02)
# ══════════════════════════════════════════════════════════════════════════════

class FormularioGenero(forms.ModelForm):
    """
    ModelForm para crear y editar géneros cinematográficos (RF-A02).

    Aprovecha la validación automática de unicidad que Django hereda del
    campo unique=True del modelo Genero. Si se intenta duplicar un nombre,
    Django lanza un ValidationError antes de llegar a save().
    """

    class Meta:
        # Modelo asociado al formulario
        model = Genero

        # Campos expuestos en el formulario
        fields = ['descripcion']

        # Etiquetas en español
        labels = {
            'descripcion': 'Nombre del género',
        }

        # Widgets con IDs únicos para el panel
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'id':          'campo-genero-descripcion',
                'placeholder': 'Ej: Acción, Comedia, Terror...',
                'autocomplete':'off',
                'maxlength':   '100',
                'class':       'modal-input',
            }),
        }

        # Mensajes de error personalizados en español
        error_messages = {
            'descripcion': {
                'unique':     'Ya existe un género con ese nombre.',
                'required':   'El nombre del género es obligatorio.',
                'max_length': 'El nombre del género no puede tener más de 100 caracteres.',
            },
        }


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE PELÍCULA (RF-A02)
# ══════════════════════════════════════════════════════════════════════════════

class FormularioPelicula(forms.ModelForm):
    """
    ModelForm para crear y editar películas (RF-A02).

    Campos:
        - titulo:            Nombre comercial del filme.
        - sinopsis:          Descripción argumental.
        - duracion_minutos:  Duración en minutos (entero positivo > 0).
        - clasificacion:     Restricción etaria (choices del modelo).
        - generos:           Relación M2M con Genero (CheckboxSelectMultiple).
        - es_clasica:        Indicador para Cine Club.
        - imagen_poster:     Archivo de imagen del póster (opcional).

    IMPORTANTE: La plantilla debe incluir enctype="multipart/form-data"
    para que Django procese correctamente el campo imagen_poster.
    """

    class Meta:
        # Modelo asociado al formulario
        model = Pelicula

        # Campos expuestos
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

        # Etiquetas en español
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

        # Widgets personalizados para el panel admin
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
            # CheckboxSelectMultiple: más intuitivo que el multi-select estándar
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

        # Mensajes de error personalizados
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
        """
        Validación personalizada: la duración debe ser mayor a 0.

        Django ya valida que sea un entero positivo (PositiveIntegerField),
        pero este método agrega un mensaje de error más claro y explícito.
        """
        duracion = self.cleaned_data.get('duracion_minutos')

        if duracion is not None and duracion <= 0:
            raise ValidationError('La duración debe ser mayor a 0 minutos.')

        return duracion


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE FUNCIÓN / PROYECCIÓN (RF-A02)
# ══════════════════════════════════════════════════════════════════════════════

class FormularioFuncion(forms.ModelForm):
    """
    ModelForm para programar funciones (proyecciones) en una sala (RF-A02).

    Campos:
        - pelicula:       FK hacia la película a proyectar.
        - sala:           FK hacia la sala (filtrado a solo 'activas' en __init__).
        - fecha:          Fecha de la función (DATE).
        - hora_inicio:    Hora de inicio de la proyección (TIME).
        - precio_entrada: Precio del ticket para esta función (Decimal).

    Validación de superposición horaria (método clean()):
        Verifica que el rango temporal de la nueva función (hora_inicio → hora_fin)
        no se solape con ninguna función ya existente en la misma sala y fecha.
        La hora_fin se calcula como: hora_inicio + duracion_minutos de la película.

        Lógica: A se superpone con B si A.inicio < B.fin Y A.fin > B.inicio.

        Si se edita una función existente (instance.pk no es None), se excluye
        la propia función de la verificación para no bloquearse a sí misma.
    """

    class Meta:
        # Modelo asociado al formulario
        model = Funcion

        # Campos expuestos
        fields = [
            'pelicula',
            'sala',
            'fecha',
            'hora_inicio',
            'precio_entrada',
        ]

        # Etiquetas en español
        labels = {
            'pelicula':       'Película',
            'sala':           'Sala',
            'fecha':          'Fecha de la función',
            'hora_inicio':    'Hora de inicio',
            'precio_entrada': 'Precio de entrada ($)',
        }

        # Widgets personalizados
        widgets = {
            'pelicula': forms.Select(attrs={
                'id': 'campo-funcion-pelicula',
            }),
            'sala': forms.Select(attrs={
                'id': 'campo-funcion-sala',
            }),
            # type="date" activa el selector nativo del navegador
            'fecha': forms.DateInput(
                attrs={
                    'id':   'campo-funcion-fecha',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            # type="time" activa el selector de hora nativo
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

        # Mensajes de error personalizados
        error_messages = {
            'pelicula':  { 'required': 'Seleccioná una película.' },
            'sala':      { 'required': 'Seleccioná una sala.' },
            'fecha':     { 'required': 'Ingresá la fecha de la función.', 'invalid': 'Ingresá una fecha válida.' },
            'hora_inicio': { 'required': 'Ingresá la hora de inicio.', 'invalid': 'Ingresá una hora válida.' },
            'precio_entrada': { 'required': 'Ingresá el precio de la entrada.', 'invalid': 'Ingresá un precio válido (ej: 3500.00).' },
        }

    def __init__(self, *args, **kwargs):
        """
        Sobreescritura de __init__ para filtrar salas activas.

        Solo se muestran en el select las salas con estado 'activa'.
        Las salas en mantenimiento no pueden asignarse a funciones nuevas.
        """
        super().__init__(*args, **kwargs)

        # Filtrar el queryset del campo 'sala' a solo salas operativas
        self.fields['sala'].queryset     = Sala.objects.filter(estado='activa')
        self.fields['pelicula'].empty_label = '--- Seleccioná una película ---'
        self.fields['sala'].empty_label     = '--- Seleccioná una sala ---'

    def clean(self):
        """
        Validaciones a nivel de formulario para Funcion:

        1. FECHA NO PASADA: No se puede programar una función en una fecha anterior a hoy.
        2. HORA NO PASADA: Si la fecha es hoy, la hora de inicio debe ser posterior a la hora actual.
        3. SUPERPOSICIÓN HORARIA: La nueva función no puede coincidir con otra función
           ya programada en la misma sala y día.
        """
        from django.utils import timezone

        # Llamar al método padre para ejecutar validaciones de campo individuales
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
                # Hora actual en la zona horaria del servidor
                hora_actual = timezone.localtime(timezone.now()).time()
                if hora_inicio <= hora_actual:
                    self.add_error(
                        'hora_inicio',
                        f'La función es para hoy. La hora de inicio debe ser posterior '
                        f'a la hora actual ({hora_actual:%H:%M}).'
                    )

        # ── Validación 3: Superposición horaria ─────────────────────────────────
        # Solo validar si todos los campos necesarios están presentes y son válidos
        if sala and fecha and hora_inicio and pelicula:

            # Calcular la hora de fin de la nueva función
            inicio_dt = datetime.combine(fecha, hora_inicio)
            fin_dt    = inicio_dt + timedelta(minutes=pelicula.duracion_minutos)
            hora_fin  = fin_dt.time()

            # Obtener funciones existentes en la misma sala y fecha
            funciones_existentes = Funcion.objects.filter(sala=sala, fecha=fecha)

            # Si editamos una función existente, excluirla de la verificación
            # para que no se bloquee consigo misma al guardar sin cambiar horario
            if self.instance and self.instance.pk:
                funciones_existentes = funciones_existentes.exclude(pk=self.instance.pk)

            for funcion_existente in funciones_existentes:

                # Calcular la hora de fin de la función existente
                inicio_exist_dt = datetime.combine(fecha, funcion_existente.hora_inicio)
                fin_exist_dt    = inicio_exist_dt + timedelta(
                    minutes=funcion_existente.pelicula.duracion_minutos
                )
                hora_fin_exist = fin_exist_dt.time()

                # Condición de superposición de intervalos:
                # A solapa B si A.inicio < B.fin  Y  A.fin > B.inicio
                hay_superposicion = (hora_inicio < hora_fin_exist) and (hora_fin > funcion_existente.hora_inicio)

                if hay_superposicion:
                    raise ValidationError(
                        f'Conflicto de horario: la sala "{sala.nombre_sala}" ya tiene '
                        f'"{funcion_existente.pelicula.titulo}" de '
                        f'{funcion_existente.hora_inicio:%H:%M} a {hora_fin_exist:%H:%M}. '
                        f'La nueva función duraría hasta las {hora_fin:%H:%M}.'
                    )

        return datos

