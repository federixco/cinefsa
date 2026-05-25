# modelos/__init__.py — Paquete raíz de modelos del proyecto.
# Los modelos se organizan en sub-paquetes temáticos:
#   modelos/contenido/  → Pelicula, Genero
#   modelos/sala/       → Sala, Asiento
#   modelos/funcion/    → Funcion
#   modelos/ventas/     → Venta, Ticket

from .identidad.usuario import Usuario, Cliente, Empleado, Administrador

from .sala.sala import Sala
from .sala.asiento import Asiento

from .contenido.genero import Genero
from .contenido.pelicula import Pelicula

from .funcion.funcion import Funcion

from .ventas.venta import Venta
from .ventas.ticket import Ticket
