"""
panel.py — Re-exportación de formularios del panel (compatibilidad retroactiva).

Los formularios fueron modularizados en archivos temáticos:
    - formularios/usuarios.py    → FormularioBusquedaUsuario, FormularioAsignarEmpleado
    - formularios/cartelera.py   → FormularioGenero, FormularioPelicula, FormularioFuncion
    - formularios/votaciones.py  → FormularioEncuesta

Este archivo re-exporta todo para no romper imports existentes.
"""

from formularios.usuarios import FormularioBusquedaUsuario, FormularioAsignarEmpleado
from formularios.cartelera import FormularioGenero, FormularioPelicula, FormularioFuncion
from formularios.votaciones import FormularioEncuesta
