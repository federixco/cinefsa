"""
models.py — Puente de re-exportación de modelos para Django.
Django busca los modelos de una app en el archivo 'app/models.py'.
Como nuestros modelos están en la carpeta 'modelos/' (estructura personalizada),
este archivo se encarga de importarlos y re-exportarlos para que Django
los descubra correctamente al ejecutar 'makemigrations' y 'migrate'.
Cada vez que se cree un nuevo modelo en 'modelos/', debe agregarse un import aquí.
"""

# ─── Modelos de Identidad y Roles (Usuarios) ─────────────────────────────────
from modelos.identidad.usuario import Usuario, Cliente, Empleado, Administrador

# ─── Modelos de Contenido (Películas y Géneros) ──────────────────────────────
from modelos.contenido.genero import Genero
from modelos.contenido.pelicula import Pelicula

# ─── Modelos de Infraestructura (Salas y Asientos) ───────────────────────────
from modelos.sala.sala import Sala
from modelos.sala.asiento import Asiento

# ─── Modelos de Programación (Funciones) ─────────────────────────────────────
from modelos.funcion.funcion import Funcion

# ─── Modelos de Votación / Cine Club (RF-C04 y RF-A04) ───────────────────────
from modelos.votacion.votacion import Encuesta, Voto

# ─── Modelos de Ventas (Transacciones y Tickets) ─────────────────────────────
from modelos.ventas.venta import Venta
from modelos.ventas.ticket import Ticket

