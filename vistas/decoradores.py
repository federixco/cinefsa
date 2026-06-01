"""
decoradores.py — Decoradores de control de acceso por rol.

Permiten restringir vistas a usuarios con roles específicos
(Empleado, Administrador) verificando la existencia del registro
en la tabla correspondiente.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def solo_empleado(view_func):
    """
    Decorador que restringe el acceso a usuarios con rol Empleado.
    Verifica que exista un registro en la tabla 'empleado' vinculado al usuario.
    Si no es empleado, redirige al inicio con un mensaje de error.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Import local para evitar imports circulares
        from sistema_cine.models import Empleado
        
        if not request.user.is_authenticated:
            return redirect('autenticacion:login')
        
        es_empleado = Empleado.objects.filter(
            usuario_id_usuario=request.user
        ).exists()
        
        if not es_empleado:
            messages.error(request, 'No tenés permisos para acceder a esta sección.')
            return redirect('inicio')
        
        return view_func(request, *args, **kwargs)
    return wrapper
