"""
autenticacion.py — Formularios de autenticación del sistema CineFSA.

Define los formularios de registro y login utilizados por las vistas
de autenticación (vistas/autenticacion/views.py). Cada formulario
hereda de las clases base de Django para aprovechar la validación
automática de contraseñas y la protección CSRF.

Formularios:
    - FormularioRegistro: Creación de cuenta nueva (Usuario + Cliente).
    - FormularioLogin: Inicio de sesión con email y contraseña.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from sistema_cine.models import Usuario


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE REGISTRO
# ══════════════════════════════════════════════════════════════════════════════

class FormularioRegistro(UserCreationForm):
    """
    Formulario de registro para nuevos clientes del portal web.

    Extiende UserCreationForm de Django (que provee validación de contraseñas)
    y agrega los campos específicos del modelo lógico: nombre_completo,
    email y fecha_nacimiento.

    Al completarse exitosamente, crea un registro en la tabla 'usuario'.
    La creación del subtipo 'cliente' (con fecha_nacimiento) se maneja
    en la vista (registro_view), no aquí, para mantener la separación
    de responsabilidades.
    """

    # ─── CAMPOS DEL FORMULARIO ────────────────────────────────────────────────

    nombre_completo = forms.CharField(
        max_length=150,
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Juan Pérez',
            'autofocus': True,
        }),
        help_text='Tu nombre y apellido como figuran en tu DNI.',
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ej: juan@email.com',
        }),
        help_text='Será tu usuario para iniciar sesión.',
    )

    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'type': 'date',
        }),
        help_text='Necesaria para verificar acceso a películas con restricción de edad.',
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres',
        }),
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repetí tu contraseña',
        }),
    )

    # ─── CONFIGURACIÓN DEL FORMULARIO ─────────────────────────────────────────

    class Meta:
        model = Usuario
        fields = ['nombre_completo', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """
        Guarda el Usuario en la base de datos.

        Auto-genera el campo 'username' a partir del email, ya que
        AbstractUser lo requiere técnicamente pero nuestro sistema
        no lo utiliza (el login se realiza exclusivamente con email).
        """
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULARIO DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class FormularioLogin(AuthenticationForm):
    """
    Formulario de inicio de sesión personalizado.

    Sobreescribe el formulario de autenticación de Django para:
        - Cambiar el campo 'username' a un input de tipo email.
        - Traducir las etiquetas y placeholders al español.

    La autenticación real se delega al backend de Django, que utiliza
    USERNAME_FIELD = 'email' (definido en el modelo Usuario) para
    verificar las credenciales contra la tabla 'usuario'.
    """

    # Se sobreescribe 'username' (nombre interno de Django) para que
    # se renderice como campo de email en el HTML.
    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@email.com',
            'autofocus': True,
        }),
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Tu contraseña',
        }),
    )
