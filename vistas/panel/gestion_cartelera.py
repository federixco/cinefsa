"""
gestion_cartelera.py — Vistas del panel de gestión de cartelera (RF-A02).
Importa el decorador @solo_administrador desde gestion_usuarios.py (mismo paquete).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from sistema_cine.models import Genero, Pelicula, Funcion
from formularios.panel import FormularioGenero, FormularioPelicula, FormularioFuncion

# Reutilizar el decorador de seguridad ya definido en el paquete
from vistas.panel.gestion_usuarios import solo_administrador


# ══════ GÉNEROS ══════════════════════════════════════════════════════════════

@solo_administrador
def listar_generos_view(request):
    """Lista todos los géneros existentes en la base de datos."""
    generos = Genero.objects.all()
    return render(request, 'panel/gestion_generos.html', {
        'generos':       generos,
        'titulo_pagina': 'Gestión de Géneros',
    })



@solo_administrador
def editar_genero_view(request, genero_id):
    """
    GET: muestra formulario prellenado con datos del género.
    POST: guarda los cambios y redirige al listado.
    """
    genero = get_object_or_404(Genero, pk=genero_id)

    if request.method == 'POST':
        formulario_genero = FormularioGenero(request.POST, instance=genero)
        if formulario_genero.is_valid():
            formulario_genero.save()
            messages.success(request, f'El género "{genero.descripcion}" fue actualizado.')
            return redirect('panel:listar_generos')
        else:
            messages.error(request, 'Corregí los errores antes de guardar.')
    else:
        formulario_genero = FormularioGenero(instance=genero)

    return render(request, 'panel/editar_genero.html', {
        'formulario_genero': formulario_genero,
        'genero':            genero,
        'titulo_pagina':     f'Editar género: {genero.descripcion}',
    })


@solo_administrador
def eliminar_genero_view(request, genero_id):
    """Elimina un género (solo POST). Las películas asociadas no se borran."""
    if request.method != 'POST':
        return redirect('panel:listar_generos')
    genero = get_object_or_404(Genero, pk=genero_id)
    nombre = genero.descripcion
    genero.delete()
    messages.success(request, f'El género "{nombre}" fue eliminado correctamente.')
    return redirect('panel:listar_generos')


# ══════ PELÍCULAS ═════════════════════════════════════════════════════════════

@solo_administrador
def listar_peliculas_view(request):
    """
    Lista películas filtradas por estado.
    Soporta ?filtro=cartelera|proximamente|retirada|todos (GET param).
    Envía a la plantilla los grupos separados para las tabs y el filtro activo.
    prefetch_related evita N+1 queries para géneros (M2M) y funciones (FK inversa).
    """
    filtro_activo = request.GET.get('filtro', 'todos')

    # Obtener base QuerySet con relaciones optimizadas
    base_qs = Pelicula.objects.prefetch_related('generos', 'funciones')

    # Filtrar según el parámetro GET
    if filtro_activo == 'cartelera':
        peliculas = base_qs.filter(estado='cartelera')
    elif filtro_activo == 'proximamente':
        peliculas = base_qs.filter(estado='proximamente')
    elif filtro_activo == 'retirada':
        peliculas = base_qs.filter(estado='retirada')
    else:
        # 'todos': mostrar todas (orden: cartelera, luego próximamente, luego retiradas)
        filtro_activo = 'todos'
        peliculas = base_qs.all()

    # Contadores por estado para los badges de las tabs
    conteo_cartelera    = base_qs.filter(estado='cartelera').count()
    conteo_proximamente = base_qs.filter(estado='proximamente').count()
    conteo_retirada     = base_qs.filter(estado='retirada').count()
    conteo_total        = base_qs.count()

    return render(request, 'panel/gestion_peliculas.html', {
        'peliculas':            peliculas,
        'filtro_activo':        filtro_activo,
        'conteo_cartelera':     conteo_cartelera,
        'conteo_proximamente':  conteo_proximamente,
        'conteo_retirada':      conteo_retirada,
        'conteo_total':         conteo_total,
        'titulo_pagina':        'Gestión de Películas',
    })


@solo_administrador
def crear_pelicula_view(request):
    """
    GET: formulario vacío de creación.
    POST: procesa incluyendo request.FILES para el póster.
    La plantilla DEBE incluir enctype="multipart/form-data".
    """
    if request.method == 'POST':
        formulario_pelicula = FormularioPelicula(request.POST, request.FILES)
        if formulario_pelicula.is_valid():
            nueva = formulario_pelicula.save()
            messages.success(request, f'"{nueva.titulo}" fue creada correctamente.')
            return redirect('panel:listar_peliculas')
        else:
            messages.error(request, 'Corregí los errores del formulario antes de guardar.')
    else:
        formulario_pelicula = FormularioPelicula()

    return render(request, 'panel/formulario_pelicula.html', {
        'formulario_pelicula': formulario_pelicula,
        'titulo_pagina':       'Nueva Película',
        'modo':                'crear',
    })


@solo_administrador
def editar_pelicula_view(request, pelicula_id):
    """
    GET: formulario prellenado (géneros M2M pre-seleccionados, póster visible).
    POST: actualiza. Si se sube nuevo póster reemplaza, si se limpia elimina.
    """
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)

    if request.method == 'POST':
        formulario_pelicula = FormularioPelicula(request.POST, request.FILES, instance=pelicula)
        if formulario_pelicula.is_valid():
            formulario_pelicula.save()
            messages.success(request, f'"{pelicula.titulo}" fue actualizada correctamente.')
            return redirect('panel:listar_peliculas')
        else:
            messages.error(request, 'Corregí los errores del formulario antes de guardar.')
    else:
        formulario_pelicula = FormularioPelicula(instance=pelicula)

    return render(request, 'panel/formulario_pelicula.html', {
        'formulario_pelicula': formulario_pelicula,
        'pelicula':            pelicula,
        'titulo_pagina':       f'Editar: {pelicula.titulo}',
        'modo':                'editar',
    })


@solo_administrador
def eliminar_pelicula_view(request, pelicula_id):
    """
    Elimina la película y sus funciones (CASCADE del modelo).
    Informa cuántas funciones fueron eliminadas en el mensaje flash.
    """
    if request.method != 'POST':
        return redirect('panel:listar_peliculas')

    pelicula           = get_object_or_404(Pelicula, pk=pelicula_id)
    cantidad_funciones = pelicula.funciones.count()
    titulo             = pelicula.titulo
    pelicula.delete()

    if cantidad_funciones > 0:
        messages.success(request,
            f'"{titulo}" fue eliminada junto con {cantidad_funciones} función(es) asociada(s).')
    else:
        messages.success(request, f'"{titulo}" fue eliminada correctamente.')

    return redirect('panel:listar_peliculas')


# ══════ FUNCIONES ═════════════════════════════════════════════════════════════

@solo_administrador
def listar_funciones_view(request):
    """
    Lista funciones separadas en próximas (cartelera activa) y pasadas (historial).
    select_related optimiza las FK de pelicula y sala.
    """
    from django.utils import timezone
    hoy = timezone.localdate()

    funciones_proximas = Funcion.objects.select_related('pelicula', 'sala').filter(fecha__gte=hoy)
    funciones_pasadas  = Funcion.objects.select_related('pelicula', 'sala').filter(fecha__lt=hoy)

    return render(request, 'panel/gestion_funciones.html', {
        'funciones_proximas': funciones_proximas,
        'funciones_pasadas':  funciones_pasadas,
        'titulo_pagina':      'Gestión de Funciones',
    })


@solo_administrador
def crear_funcion_view(request):
    """
    Programa una nueva función. El clean() del formulario detecta
    automáticamente los conflictos de superposición horaria.
    """
    if request.method == 'POST':
        formulario_funcion = FormularioFuncion(request.POST)
        if formulario_funcion.is_valid():
            f = formulario_funcion.save()
            messages.success(request,
                f'Función de "{f.pelicula.titulo}" en "{f.sala.nombre_sala}" '
                f'el {f.fecha:%d/%m/%Y} a las {f.hora_inicio:%H:%M} programada correctamente.')
            return redirect('panel:listar_funciones')
        else:
            messages.error(request, 'No se pudo programar la función. Revisá los errores.')
    else:
        formulario_funcion = FormularioFuncion()

    return render(request, 'panel/formulario_funcion.html', {
        'formulario_funcion': formulario_funcion,
        'titulo_pagina':      'Nueva Función',
        'modo':               'crear',
    })


@solo_administrador
def editar_funcion_view(request, funcion_id):
    """
    Edita una función. La verificación de superposición excluye
    la propia función (instance.pk) para no bloquearse a sí misma.
    """
    funcion = get_object_or_404(Funcion, pk=funcion_id)

    if request.method == 'POST':
        formulario_funcion = FormularioFuncion(request.POST, instance=funcion)
        if formulario_funcion.is_valid():
            formulario_funcion.save()
            messages.success(request,
                f'La función de "{funcion.pelicula.titulo}" fue actualizada correctamente.')
            return redirect('panel:listar_funciones')
        else:
            messages.error(request, 'No se pudo actualizar la función. Revisá los errores.')
    else:
        formulario_funcion = FormularioFuncion(instance=funcion)

    return render(request, 'panel/formulario_funcion.html', {
        'formulario_funcion': formulario_funcion,
        'funcion':            funcion,
        'titulo_pagina':      f'Editar Función: {funcion.pelicula.titulo}',
        'modo':               'editar',
    })


@solo_administrador
def eliminar_funcion_view(request, funcion_id):
    """Elimina una función programada (solo POST)."""
    if request.method != 'POST':
        return redirect('panel:listar_funciones')

    funcion         = get_object_or_404(Funcion, pk=funcion_id)
    titulo_pelicula = funcion.pelicula.titulo
    nombre_sala     = funcion.sala.nombre_sala
    fecha_f         = funcion.fecha
    hora_f          = funcion.hora_inicio
    funcion.delete()

    messages.success(request,
        f'La función de "{titulo_pelicula}" en "{nombre_sala}" '
        f'del {fecha_f:%d/%m/%Y} a las {hora_f:%H:%M} fue eliminada.')
    return redirect('panel:listar_funciones')
