"""
usuarios.py — Formularios de gestión de usuarios (RF-A05).

Formularios:
    - FormularioBusquedaUsuario: Campo de texto para buscar usuarios
      registrados por nombre completo o dirección de email.
    - FormularioAsignarEmpleado: Campos necesarios para crear el registro
      en la tabla 'empleado': terminal_venta (id_validador se auto-genera).
"""

from django import forms


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
        required=False,
        label='Buscar usuario',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre completo o email del usuario...',
            'id': 'campo-busqueda-usuario',
            'autocomplete': 'off',
        }),
    )


class FormularioAsignarEmpleado(forms.Form):
    """
    Formulario para asignar el rol de Empleado a un usuario (RF-A05).

    Campos:
        - id_validador:   Código único del empleado para el sistema de validación QR.
        - terminal_venta: Número de la terminal/caja asignada al empleado (entero positivo).
    """

    id_validador = forms.CharField(
        required=False,
        max_length=50,
        label='ID de validador (QR)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Se auto-generará (ej. EMP-0001)',
            'id': 'campo-id-validador',
            'readonly': 'readonly',
        }),
        help_text=(
            'Código único que identifica al empleado en el sistema de '
            'validación de entradas QR en la puerta de acceso.'
        ),
    )

    terminal_venta = forms.IntegerField(
        min_value=1,
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
