"""
gestion_usuarios.py — Vistas del panel de gestión de usuarios (RF-A05).

Implementa el requerimiento RF-A05 (Gestión de Usuarios y Permisos):
    - El Administrador puede buscar usuarios registrados en la plataforma.
    - Puede elevar el privilegio de un usuario asignándole el rol 'Empleado'.
    - Puede revocar ese privilegio eliminando el registro de Empleado.

Protección de acceso:
    Todas las vistas usan el decorador @solo_administrador que verifica
    que el usuario logueado tenga un registro en la tabla 'administrador'.
    Si no lo tiene, es redirigido al inicio con un mensaje de error.

Flujo de asignación de rol (POST /panel/usuarios/asignar/):
    1. Se recibe el ID del usuario objetivo y los datos del formulario.
    2. Se verifica que el usuario no sea ya un Administrador.
    3. Se verifica que no tenga ya un registro de Empleado.
    4. Se crea el registro en la tabla 'empleado' con id_validador y terminal_venta.

Flujo de revocación de rol (POST /panel/usuarios/revocar/):
    1. Se recibe el ID del usuario objetivo.
    2. Se busca su registro en la tabla 'empleado'.
    3. Si existe, se elimina. El usuario sigue siendo Cliente (no se borra).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import functools

from sistema_cine.models import Usuario, Empleado, Administrador
from formularios.panel import FormularioBusquedaUsuario, FormularioAsignarEmpleado


# ══════════════════════════════════════════════════════════════════════════════
#  DECORADOR DE PROTECCIÓN: SOLO ADMINISTRADOR
# ══════════════════════════════════════════════════════════════════════════════

def solo_administrador(funcion_vista):
    """
    Decorador que restringe el acceso exclusivamente a Administradores.

    Combina dos verificaciones en orden:
        1. @login_required implícito: si el usuario no está logueado, redirige
           automáticamente a LOGIN_URL (definido en configuracion.py).
        2. Verificación de rol: comprueba si el usuario logueado tiene un
           registro en la tabla 'administrador'. Si no lo tiene (es decir,
           es un cliente o empleado), redirige al inicio con mensaje de error.

    Uso:
        @solo_administrador
        def mi_vista(request):
            ...

    Esto garantiza que ningún cliente ni empleado pueda acceder al panel,
    incluso si conoce la URL directamente.
    """
    @login_required  # Paso 1: verificar que el usuario esté autenticado
    @functools.wraps(funcion_vista)  # Preserva el nombre y docstring de la vista original
    def vista_protegida(request, *args, **kwargs):
        # Paso 2: verificar que el usuario tenga registro en la tabla 'administrador'
        # La relación inversa 'administrador' viene del related_name del modelo Administrador
        tiene_rol_admin = Administrador.objects.filter(
            usuario_id_usuario=request.user
        ).exists()

        if not tiene_rol_admin:
            # El usuario existe pero no es administrador → acceso denegado
            messages.error(
                request,
                'Acceso denegado. Esta sección es exclusiva para administradores.'
            )
            return redirect('inicio')

        # Si pasó ambas verificaciones, ejecutar la vista normalmente
        return funcion_vista(request, *args, **kwargs)

    return vista_protegida


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA PRINCIPAL: PANEL DE GESTIÓN DE USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
def panel_usuarios_view(request):
    """
    Vista principal del panel de gestión de usuarios (RF-A05).

    GET:
        Carga TODOS los usuarios registrados al entrar a la página.
        Soporta dos filtros combinables via parámetros GET:
            - ?busqueda=texto  → filtra por nombre completo o email (parcial, case-insensitive).
            - ?rol=cliente|empleado|admin  → filtra por rol actual del usuario.
        Si no se envía ningún filtro, se muestran todos los usuarios.

    Contexto enviado a la plantilla:
        - formulario_asignar: instancia del FormularioAsignarEmpleado (modal de asignación).
        - usuarios: lista de diccionarios con info del usuario + su rol actual.
        - termino_busqueda: el texto ingresado (para mantenerlo en el input).
        - filtro_rol: el filtro de rol activo ('todos', 'cliente', 'empleado', 'admin').
        - stats: diccionario con contadores por rol para las tarjetas de estadísticas.
    """
    # Instanciar formulario de asignación (para el modal de "Asignar como Empleado")
    formulario_asignar = FormularioAsignarEmpleado()

    # ── Leer filtros GET ──
    termino_busqueda = request.GET.get('busqueda', '').strip()
    filtro_rol = request.GET.get('rol', 'todos')

    # ── Estadísticas globales (siempre se calculan, independientes de los filtros) ──
    ids_empleados = set(Empleado.objects.values_list('usuario_id_usuario_id', flat=True))
    ids_admins = set(Administrador.objects.values_list('usuario_id_usuario_id', flat=True))
    total_usuarios = Usuario.objects.count()

    stats = {
        'total': total_usuarios,
        'empleados': len(ids_empleados),
        'admins': len(ids_admins),
        'clientes': total_usuarios - len(ids_empleados) - len(ids_admins),
    }

    # ── Construir queryset base (todos los usuarios) ──
    usuarios_queryset = Usuario.objects.all().order_by('nombre_completo')

    # Filtro por búsqueda de texto (nombre o email)
    if termino_busqueda:
        usuarios_queryset = usuarios_queryset.filter(
            Q(nombre_completo__icontains=termino_busqueda) |
            Q(email__icontains=termino_busqueda)
        )

    # Filtro por rol
    if filtro_rol == 'empleado':
        usuarios_queryset = usuarios_queryset.filter(id__in=ids_empleados)
    elif filtro_rol == 'admin':
        usuarios_queryset = usuarios_queryset.filter(id__in=ids_admins)
    elif filtro_rol == 'cliente':
        usuarios_queryset = usuarios_queryset.exclude(
            id__in=ids_empleados | ids_admins
        )

    # ── Enriquecer cada usuario con info de rol ──
    usuarios_con_roles = []
    for usuario in usuarios_queryset:
        es_empleado_obj = None
        if usuario.id in ids_empleados:
            es_empleado_obj = Empleado.objects.filter(
                usuario_id_usuario=usuario
            ).first()

        usuarios_con_roles.append({
            'usuario': usuario,
            'es_empleado': es_empleado_obj,
            'es_administrador': usuario.id in ids_admins,
        })

    return render(request, 'panel/gestion_usuarios.html', {
        'formulario_asignar': formulario_asignar,
        'usuarios': usuarios_con_roles,
        'termino_busqueda': termino_busqueda,
        'filtro_rol': filtro_rol,
        'stats': stats,
        'titulo_pagina': 'Gestión de Usuarios y Roles',
    })


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: ASIGNAR ROL DE EMPLEADO
# ══════════════════════════════════════════════════════════════════════════════

def _generar_id_validador():
    """
    Genera el próximo id_validador en formato emp-XXX llamando
    al procedimiento almacenado de la base de datos (sp_generar_id_validador).

    Retorna:
        str: Código generado por MySQL, por ejemplo 'emp-001'.
    """
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("CALL sp_generar_id_validador(@nuevo_id)")
        cursor.execute("SELECT @nuevo_id")
        resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] else 'emp-001'


@solo_administrador
def asignar_empleado_view(request):
    """
    Vista para elevar el privilegio de un usuario al rol de Empleado (RF-A05).

    Solo acepta método POST (enviado desde el modal del panel).
    No tiene GET propio; si se accede directamente, redirige al panel.

    Proceso:
        1. Obtiene el usuario objetivo por su ID (404 si no existe).
        2. Verifica que no sea un Administrador (no se puede degradar a un admin).
        3. Verifica que no tenga ya un registro de Empleado (evitar duplicados).
        4. Auto-genera el id_validador en formato EMP-XXXX (secuencial).
        5. Valida el formulario con terminal_venta.
        6. Crea el registro en la tabla 'empleado'.
        7. Redirige al panel con mensaje de éxito que incluye el código generado.
    """
    if request.method != 'POST':
        return redirect('panel:gestion_usuarios')

    usuario_id = request.POST.get('usuario_id')
    usuario_objetivo = get_object_or_404(Usuario, pk=usuario_id)

    # Verificación 1: No se puede asignar el rol de empleado a otro administrador
    es_administrador = Administrador.objects.filter(
        usuario_id_usuario=usuario_objetivo
    ).exists()

    if es_administrador:
        messages.warning(
            request,
            f'No se puede asignar el rol de empleado a {usuario_objetivo.nombre_completo} '
            f'porque ya es Administrador.'
        )
        return redirect('panel:gestion_usuarios')

    # Verificación 2: No crear duplicados si ya es empleado
    ya_es_empleado = Empleado.objects.filter(
        usuario_id_usuario=usuario_objetivo
    ).exists()

    if ya_es_empleado:
        messages.warning(
            request,
            f'{usuario_objetivo.nombre_completo} ya tiene el rol de Empleado asignado.'
        )
        return redirect('panel:gestion_usuarios')

    # Validar el formulario (solo terminal_venta)
    formulario_asignar = FormularioAsignarEmpleado(request.POST)

    if formulario_asignar.is_valid():
        # Auto-generar el id_validador en formato EMP-XXXX
        id_validador = _generar_id_validador()

        Empleado.objects.create(
            usuario_id_usuario=usuario_objetivo,
            id_validador=id_validador,
            terminal_venta=formulario_asignar.cleaned_data['terminal_venta'],
        )
        messages.success(
            request,
            f'Se asignó el rol de Empleado a {usuario_objetivo.nombre_completo}. '
            f'ID de validador asignado: {id_validador}'
        )
    else:
        errores = '; '.join([
            f"{campo}: {', '.join(errs)}"
            for campo, errs in formulario_asignar.errors.items()
        ])
        messages.error(request, f'Error al asignar el rol: {errores}')

    return redirect('panel:gestion_usuarios')


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: REVOCAR ROL DE EMPLEADO
# ══════════════════════════════════════════════════════════════════════════════

@solo_administrador
def revocar_empleado_view(request):
    """
    Vista para revocar el rol de Empleado de un usuario (RF-A05).

    Solo acepta método POST. Elimina el registro de la tabla 'empleado'
    vinculado al usuario objetivo. El usuario sigue existiendo como Cliente.

    Proceso:
        1. Obtiene el usuario objetivo por su ID.
        2. Busca su registro en la tabla 'empleado'.
        3. Si existe, lo elimina.
        4. Redirige al panel con mensaje de éxito o advertencia.
    """
    if request.method != 'POST':
        # Si alguien intenta acceder por GET, redirigir al panel
        return redirect('panel:gestion_usuarios')

    # Obtener el ID del usuario objetivo desde el formulario
    usuario_id = request.POST.get('usuario_id')

    # Buscar el usuario o devolver error 404 si no existe
    usuario_objetivo = get_object_or_404(Usuario, pk=usuario_id)

    # Buscar el registro de empleado vinculado al usuario
    try:
        empleado = Empleado.objects.get(usuario_id_usuario=usuario_objetivo)
        empleado.delete()
        messages.success(
            request,
            f'Se revocó el rol de Empleado de {usuario_objetivo.nombre_completo} correctamente. '
            f'El usuario sigue siendo Cliente del sistema.'
        )
    except Empleado.DoesNotExist:
        # El usuario no tenía rol de empleado (caso inesperado)
        messages.warning(
            request,
            f'{usuario_objetivo.nombre_completo} no tenía el rol de Empleado asignado.'
        )

    return redirect('panel:gestion_usuarios')
