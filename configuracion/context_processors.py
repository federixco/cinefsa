"""
context_processors.py — Procesadores de contexto globales de CineFSA.

Inyectan variables calculadas en TODOS los templates del sistema,
disponibles sin necesidad de pasarlas manualmente desde cada vista.
"""

from sistema_cine.models import Empleado


def roles_usuario(request):
    """
    Inyecta la variable `es_empleado` en todos los templates.

    Calcula si el usuario autenticado tiene un registro en la tabla
    'empleado' mediante una consulta directa a la base de datos,
    evitando el uso de RelatedManager (ForeignKey) en templates que
    podría generar comportamientos inesperados.

    Variables inyectadas:
        - es_empleado (bool): True si el usuario tiene rol de Empleado.
    """
    es_empleado = False

    if request.user.is_authenticated:
        es_empleado = Empleado.objects.filter(
            usuario_id_usuario=request.user
        ).exists()

    return {
        'es_empleado': es_empleado,
    }
