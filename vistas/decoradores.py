"""
decoradores.py — Decoradores de control de acceso por rol.

Permiten restringir vistas a usuarios con roles específicos
(Empleado, Administrador) verificando la existencia del registro
en la tabla correspondiente.

Decoradores disponibles:
    - solo_empleado: Restringe acceso a usuarios con rol Empleado.
    - solo_administrador: Restringe acceso a usuarios con rol Administrador.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
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


def solo_administrador(funcion_vista):
    """
    Decorador que restringe el acceso exclusivamente a Administradores.

    Combina dos verificaciones en orden:
        1. @login_required implícito: si el usuario no está logueado, redirige
           automáticamente a LOGIN_URL (definido en configuracion.py).
        2. Verificación de rol: comprueba si el usuario logueado tiene un
           registro en la tabla 'administrador'. Si no lo tiene, redirige
           al inicio con mensaje de error.
    """
    @login_required
    @wraps(funcion_vista)
    def vista_protegida(request, *args, **kwargs):
        from sistema_cine.models import Administrador

        tiene_rol_admin = Administrador.objects.filter(
            usuario_id_usuario=request.user
        ).exists()

        if not tiene_rol_admin:
            messages.error(
                request,
                'Acceso denegado. Esta sección es exclusiva para administradores.'
            )
            return redirect('inicio')

        return funcion_vista(request, *args, **kwargs)

    return vista_protegida
