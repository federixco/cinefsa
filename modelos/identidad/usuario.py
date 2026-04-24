"""
usuario.py — Modelos de identidad y roles del sistema CineFSA.

Define la jerarquía de usuarios mediante una estrategia de especialización:
    - Usuario: Supertipo que extiende AbstractUser de Django. Contiene los
      atributos comunes a todos los actores del sistema según el modelo
      lógico: nombre_completo, password_hash (manejado por Django),
      fecha_registro y email.
    - Cliente: Subtipo con PK propia (id_cliente) y FK hacia usuario.
    - Empleado: Subtipo con PK propia (id_empleado) y FK hacia usuario.
    - Administrador: Subtipo con PK propia (id_admin) y FK hacia usuario.

Relación con el modelo lógico (TP2):
    Cada subtipo tiene su propia clave primaria y una FK hacia la tabla
    'usuario', reproduciendo exactamente el esquema relacional del diagrama.
    Se respetan los nombres de columna: usuario_id_usuario como FK en
    cada subtipo.

Nota sobre AbstractUser:
    Django requiere AbstractUser para proveer el sistema de sesiones, login,
    logout y cifrado de contraseñas. Esto agrega internamente columnas extra
    (username, is_staff, etc.) que no figuran en el modelo lógico pero no
    interfieren con la lógica del sistema. No se usan en ninguna pantalla.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


# ══════════════════════════════════════════════════════════════════════════════
#  SUPERTIPO — USUARIO
# ══════════════════════════════════════════════════════════════════════════════

class Usuario(AbstractUser):
    """
    Entidad: usuario (Supertipo / Superclase)

    Tabla en MySQL: 'usuario'
    Columnas según modelo lógico:
        - id_usuario   → generado automáticamente por Django (PK)
        - nombre_completo
        - password_hash → manejado internamente por AbstractUser como 'password'
        - fecha_registro
        - email

    AbstractUser agrega columnas adicionales (username, is_staff, etc.)
    que no se usan en el sistema pero son necesarias técnicamente para
    el funcionamiento del motor de autenticación de Django.
    """

    # ─── CAMPOS DEL MODELO LÓGICO ─────────────────────────────────────────────

    # nombre_completo: Nombre y apellido del usuario en un único campo.
    # Reemplaza a los campos 'first_name' y 'last_name' de AbstractUser.
    nombre_completo = models.CharField(
        max_length=150,
        verbose_name='Nombre completo'
    )

    # fecha_registro: Timestamp automático del momento en que se creó la cuenta.
    # auto_now_add=True hace que Django lo complete solo al momento del INSERT.
    # El usuario nunca puede modificar este campo manualmente.
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    
    
    
    # ─── SOBREESCRITURA DE RELATED_NAMES HEREDADOS ────────────────────────────────
    # AbstractUser hereda los campos 'groups' y 'user_permissions' de PermissionsMixin.
    # Como Django también tiene su propio auth.User con los mismos related_names,
    # hay un conflicto de accessores inversos. Se sobreescriben con related_name
    # personalizados para que no choquen entre sí.
    
    groups = models.ManyToManyField(
    'auth.Group',
    blank=True,
    related_name='usuario_cine_set',
    verbose_name='Grupos'
    )
    
    user_permissions = models.ManyToManyField(
    'auth.Permission',
    blank=True,
    related_name='usuario_cine_set',
    verbose_name='Permisos'
    )


    # email: Dirección de correo electrónico única por usuario.
    # Se sobreescribe el campo email de AbstractUser para agregar unique=True.
    # Este campo actúa como identificador de login (USERNAME_FIELD).
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    
    # ─── DESACTIVACIÓN DE CAMPOS HEREDADOS NO UTILIZADOS ──────────────────────

    # Se anulan first_name y last_name porque el sistema usa 'nombre_completo'.
    first_name = None
    last_name = None

    # ─── CAMPO DE AUTENTICACIÓN ───────────────────────────────────────────────

    # USERNAME_FIELD: el login se realiza con email en lugar de username.
    # username sigue existiendo internamente (requerido por AbstractUser)
    # pero no se expone en ninguna pantalla del sistema.
    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS: campos obligatorios al crear superusuario por consola.
    # Se incluye username porque AbstractUser lo requiere técnicamente,
    # y nombre_completo porque es el identificador legible del sistema.
    REQUIRED_FIELDS = ['username', 'nombre_completo']

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre_completo']

    def __str__(self):
        """Representación en texto: 'Nombre Completo (email)'."""
        return f'{self.nombre_completo} ({self.email})'


# ══════════════════════════════════════════════════════════════════════════════
#  SUBTIPO — CLIENTE
# ══════════════════════════════════════════════════════════════════════════════

class Cliente(models.Model):
    """
    Entidad: cliente (Subtipo de Usuario)

    Tabla en MySQL: 'cliente'
    Columnas según modelo lógico:
        - id_cliente        → PK propia autoincremental
        - fecha_nacimiento  → DATE, para control de clasificación de edad
        - usuario_id_usuario → FK hacia la tabla 'usuario'

    Representa al consumidor final: el ciudadano que compra entradas
    desde el portal web o desde la boletería presencial.
    La fecha_nacimiento permite validar el acceso a películas con
    clasificación restringida (+13, +16, +18) al momento de la compra.
    """

    # id_cliente: PK propia del subtipo, autoincremental.
    # Se declara explícitamente para respetar el nombre del modelo lógico.
    id_cliente = models.AutoField(
        primary_key=True,
        verbose_name='ID Cliente'
    )

    # usuario_id_usuario: FK hacia la tabla 'usuario'.
    # db_column respeta el nombre exacto de la columna del modelo lógico.
    # on_delete=CASCADE: si se elimina el Usuario, se elimina el Cliente.
    # related_name='cliente': permite acceder desde usuario con mi_usuario.cliente
    usuario_id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='usuario_id_usuario',
        related_name='cliente',
        verbose_name='Usuario'
    )

    # fecha_nacimiento: Fecha de nacimiento del cliente.
    # Usada para calcular la edad y validar acceso a contenido restringido.
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de nacimiento'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        """Representación en texto: nombre completo del usuario vinculado."""
        return self.usuario_id_usuario.nombre_completo


# ══════════════════════════════════════════════════════════════════════════════
#  SUBTIPO — EMPLEADO
# ══════════════════════════════════════════════════════════════════════════════

class Empleado(models.Model):
    """
    Entidad: empleado (Subtipo de Usuario)

    Tabla en MySQL: 'empleado'
    Columnas según modelo lógico:
        - id_empleado        → PK propia autoincremental
        - id_validador       → VARCHAR, código único para validación QR
        - terminal_venta     → INT, número de caja asignada
        - usuario_id_usuario → FK hacia la tabla 'usuario'

    Representa al personal operativo del complejo. Puede realizar ventas
    presenciales en boletería y validar entradas QR en la puerta de acceso.
    El rol es asignado por el Administrador desde el panel de gestión (RF-A05).
    """

    # id_empleado: PK propia del subtipo, autoincremental.
    id_empleado = models.AutoField(
        primary_key=True,
        verbose_name='ID Empleado'
    )

    # usuario_id_usuario: FK hacia la tabla 'usuario'.
    usuario_id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='usuario_id_usuario',
        related_name='empleado',
        verbose_name='Usuario'
    )

    # id_validador: Código único del empleado para el sistema de validación QR.
    # Registra qué empleado validó cada entrada en la puerta de acceso.
    id_validador = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='ID de validador'
    )

    # terminal_venta: Número de la terminal/caja asignada al empleado.
    # Permite identificar desde qué punto de venta se emitió cada ticket.
    terminal_venta = models.PositiveIntegerField(
        verbose_name='Terminal de venta'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        """Representación en texto: 'Nombre (Terminal N)'."""
        return f'{self.usuario_id_usuario.nombre_completo} (Terminal {self.terminal_venta})'


# ══════════════════════════════════════════════════════════════════════════════
#  SUBTIPO — ADMINISTRADOR
# ══════════════════════════════════════════════════════════════════════════════

class Administrador(models.Model):
    """
    Entidad: administrador (Subtipo de Usuario)

    Tabla en MySQL: 'administrador'
    Columnas según modelo lógico:
        - id_admin           → PK propia autoincremental
        - nivel_gestion      → VARCHAR, define el alcance de permisos
        - usuario_id_usuario → FK hacia la tabla 'usuario'

    Representa al personal de máximo nivel jerárquico. Tiene acceso completo
    al panel de gestión: cartelera, diseño de salas, reportes de votaciones
    y administración de roles de usuarios (RF-A05).
    """

    # id_admin: PK propia del subtipo, autoincremental.
    id_admin = models.AutoField(
        primary_key=True,
        verbose_name='ID Administrador'
    )

    # usuario_id_usuario: FK hacia la tabla 'usuario'.
    usuario_id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='usuario_id_usuario',
        related_name='administrador',
        verbose_name='Usuario'
    )

    # nivel_gestion: Define el alcance de los permisos administrativos.
    # Permite escalar la jerarquía sin modificar la estructura de la BD.
    # Ejemplos de valores: 'gerente', 'supervisor', 'encargado'.
    nivel_gestion = models.CharField(
        max_length=50,
        verbose_name='Nivel de gestión'
    )

    # ─── CONFIGURACIÓN DEL MODELO ─────────────────────────────────────────────

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        """Representación en texto: 'Nombre (Nivel: nivel_gestion)'."""
        return f'{self.usuario_id_usuario.nombre_completo} (Nivel: {self.nivel_gestion})'