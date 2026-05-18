"""
panel.py — Formularios del panel de administración del sistema CineFSA.

Define los formularios usados en el panel interno de gestión,
accesible exclusivamente por el rol de Administrador (RF-A05).

Formularios:
    - FormularioBusquedaUsuario: Campo de texto para buscar usuarios
      registrados por nombre completo o dirección de email.
    - FormularioAsignarEmpleado: Campos necesarios para crear el registro
      en la tabla 'empleado': id_validador y terminal_venta.
"""

from django import forms


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

    Se muestra como un modal dentro del panel cuando el administrador
    hace clic en "Asignar como Empleado".

    Campos:
        - terminal_venta: Número de la terminal/caja asignada al empleado (entero positivo).

    Nota: El campo 'id_validador' se auto-genera en la vista con formato EMP-XXXX
    (secuencial) al momento de crear el registro. No se solicita al administrador.
    """

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
