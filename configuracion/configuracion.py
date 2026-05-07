"""
configuracion.py — Archivo de configuración principal de Django para el proyecto.

Este módulo centraliza todos los parámetros del sistema. Está organizado en secciones
temáticas para facilitar su lectura y mantenimiento a lo largo del ciclo de vida del proyecto.
"""

from pathlib import Path

# BASE_DIR: Ruta raíz del proyecto, calculada dinámicamente.
# Path(__file__) apunta a este archivo (configuracion.py).
# .resolve() convierte la ruta relativa en absoluta.
# .parent.parent sube dos niveles: de /configuración/ a la raíz del proyecto.
# Todas las rutas del proyecto se construyen a partir de esta variable.
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── SEGURIDAD ────────────────────────────────────────────────────────────────

# SECRET_KEY: Clave criptográfica usada por Django para firmar cookies, tokens CSRF
# y otras operaciones de seguridad. Debe ser única, larga y aleatoria.
# ⚠️  IMPORTANTE: En producción esta clave NUNCA debe estar hardcodeada aquí.
#     Usar python-decouple para leerla desde un archivo .env:
#     SECRET_KEY = config('SECRET_KEY')
SECRET_KEY = 'admin'

# DEBUG: Activa el modo de depuración de Django.
# En True: muestra trazas de error detalladas en el navegador (útil en desarrollo).
# ⚠️  En producción siempre debe ser False para no exponer información sensible del sistema.
DEBUG = True

# ALLOWED_HOSTS: Lista de dominios o IPs desde los que se acepta tráfico HTTP.
# En desarrollo se usan los alias locales de XAMPP / servidor de desarrollo de Django.
# En producción se agrega el dominio real del servidor (ej: 'cinefsa.com.ar').
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ─── APLICACIONES INSTALADAS ──────────────────────────────────────────────────

# INSTALLED_APPS: Registro de todas las aplicaciones activas en el proyecto.
# Django carga en orden estos módulos al iniciar el servidor.
INSTALLED_APPS = [
    'django.contrib.admin',        # Panel de administración automático de Django (/admin/).
    'django.contrib.auth',         # Sistema de autenticación: usuarios, grupos y permisos.
    'django.contrib.contenttypes', # Framework de tipos de contenido genérico (requerido por auth).
    'django.contrib.sessions',     # Manejo de sesiones de usuario en base de datos o caché.
    'django.contrib.messages',     # Sistema de mensajes flash (notificaciones temporales al usuario).
    'django.contrib.staticfiles',  # Gestión y servicio de archivos estáticos (CSS, JS, imágenes de UI).
    'sistema_cine',                # Aplicación principal del proyecto: modelos, vistas y lógica de negocio.
]


# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────

# MIDDLEWARE: Capas de procesamiento que se ejecutan en orden para cada request/response.
# Actúan como "filtros" que interceptan las peticiones antes de llegar a las vistas
# y las respuestas antes de enviarse al cliente.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',              # Aplica cabeceras HTTP de seguridad (HSTS, etc.).
    'django.contrib.sessions.middleware.SessionMiddleware',       # Habilita el uso de sesiones en las vistas.
    'django.middleware.common.CommonMiddleware',                  # Normaliza URLs (agrega trailing slash, etc.).
    'django.middleware.csrf.CsrfViewMiddleware',                  # Protege formularios contra ataques CSRF.
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # Asocia el usuario autenticado al request (request.user).
    'django.contrib.messages.middleware.MessageMiddleware',       # Habilita el sistema de mensajes flash entre vistas.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',     # Previene que el sitio sea embebido en iframes externos (clickjacking).
]

# ROOT_URLCONF: Módulo Python que contiene la tabla de enrutamiento principal (urls.py).
# Cada petición HTTP llega aquí primero para ser derivada a la vista correcta.
ROOT_URLCONF = 'configuracion.urls'


# ─── MOTOR DE PLANTILLAS (TEMPLATES) ─────────────────────────────────────────

# TEMPLATES: Configuración del sistema de renderizado de HTML.
# Django usa su propio lenguaje de plantillas (DTL) para generar las vistas dinámicas
# del portal del cliente y el panel de administración.
TEMPLATES = [
    {
        # BACKEND: Motor de plantillas a utilizar. Se usa el nativo de Django (DjangoTemplates).
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # DIRS: Directorios adicionales donde Django buscará archivos .html.
        # Se apunta a la carpeta /plantillas/ en la raíz del proyecto,
        # donde se almacenarán los HTML base (base.html, portal, panel admin, etc.).
        'DIRS': [BASE_DIR / 'plantillas'],

        # APP_DIRS: Si es True, Django también busca plantillas dentro de cada
        # app en la subcarpeta templates/ (útil para el panel de admin por defecto).
        'APP_DIRS': True,

        'OPTIONS': {
            # context_processors: Funciones que inyectan variables globales en cada plantilla.
            'context_processors': [
                'django.template.context_processors.debug',    # Inyecta la variable {{ debug }}.
                'django.template.context_processors.request',  # Inyecta el objeto {{ request }} (URL actual, usuario, etc.).
                'django.contrib.auth.context_processors.auth', # Inyecta {{ user }} y {{ perms }} (roles del usuario logueado).
                'django.contrib.messages.context_processors.messages', # Inyecta {{ messages }} para mostrar notificaciones.
            ],
        },
    },
]

# WSGI_APPLICATION: Punto de entrada para servidores WSGI en producción (ej: Gunicorn, uWSGI).
# WSGI (Web Server Gateway Interface) es el protocolo estándar entre el servidor web y Django.
WSGI_APPLICATION = 'configuracion.wsgi.application'


# ─── BASE DE DATOS ────────────────────────────────────────────────────────────

# DATABASES: Configuración de la conexión a la base de datos del sistema.
# Se utiliza MySQL, gestionado a través del stack XAMPP local (Apache + MySQL).
# El motor 'mysqlclient' (instalado como dependencia) actúa como conector Python ↔ MySQL.
DATABASES = {
    'default': {
        # ENGINE: Driver de base de datos. Django soporta múltiples motores;
        # se usa MySQL por ser el estándar transaccional del proyecto.
        'ENGINE': 'django.db.backends.mysql',

        # NAME: Nombre de la base de datos a conectar en el servidor MySQL.
        # Debe ser creada previamente en phpMyAdmin o con: CREATE DATABASE sistema_cine;
        'NAME': 'sistema_cine',

        # USER / PASSWORD: Credenciales del servidor MySQL de XAMPP.
        # Por defecto XAMPP usa 'root' sin contraseña en entorno local.
        # ⚠️  En producción usar variables de entorno con python-decouple.
        'USER':     'root',
        'PASSWORD': '',

        # HOST: Dirección IP del servidor MySQL. Se usa 127.0.0.1 en lugar de 'localhost'
        # para forzar conexión TCP/IP en vez de socket Unix (más compatible con mysqlclient).
        'HOST': '127.0.0.1',

        # PORT: Puerto estándar de MySQL. XAMPP lo expone en el puerto 3306 por defecto.
        'PORT': '3306',

        'OPTIONS': {
            # charset: Codificación de caracteres de la conexión.
            # utf8mb4 es el conjunto completo de Unicode (incluye emojis y caracteres especiales),
            # necesario para almacenar correctamente nombres, sinopsis y títulos en español.
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    }
}


# ─── IDIOMA Y ZONA HORARIA ────────────────────────────────────────────────────

# LANGUAGE_CODE: Idioma predeterminado del sistema para traducciones del panel admin,
# mensajes de error de validación de formularios, etc.
# 'es-ar' = Español (Argentina).
LANGUAGE_CODE = 'es-ar'

# TIME_ZONE: Zona horaria para el almacenamiento y visualización de fechas/horas.
# Crítico para el módulo de Funciones: los horarios de proyección deben reflejar
# la hora local de Formosa (UTC-3), evitando desfasajes en la cartelera.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# USE_I18N: Activa el sistema de internacionalización (i18n) de Django.
# Permite traducir textos de la interfaz al idioma definido en LANGUAGE_CODE.
USE_I18N = True

# USE_TZ: Activa el soporte de zonas horarias conscientes (timezone-aware) en Django.
# Cuando es True, Django almacena todas las fechas en UTC en la base de datos
# y las convierte automáticamente a TIME_ZONE al mostrarlas. Recomendado siempre en True.
USE_TZ = True


# ─── ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES DE INTERFAZ) ──────────────────────

# STATIC_URL: Prefijo de URL pública para acceder a los archivos estáticos desde el navegador.
# Ejemplo: http://localhost:8000/estaticos/css/estilos.css
STATIC_URL = '/estaticos/'

# STATICFILES_DIRS: Directorios del filesystem donde Django buscará archivos estáticos
# durante el desarrollo (con collectstatic en producción). Apunta a /estaticos/ en la raíz.
# Aquí se almacenan: hojas de estilo (CSS), scripts (JS) e íconos de la interfaz.
# ⚠️  Desactivado temporalmente: se habilitará cuando se integren los estilos CSS.
# STATICFILES_DIRS = [BASE_DIR / 'estaticos']


# ─── ARCHIVOS MULTIMEDIA (SUBIDOS POR USUARIOS / ADMIN) ──────────────────────

# MEDIA_URL: Prefijo de URL pública para acceder a los archivos subidos dinámicamente.
# Ejemplo: http://localhost:8000/multimedia/posters/inception.jpg
MEDIA_URL = '/multimedia/'

# MEDIA_ROOT: Ruta absoluta en el servidor donde Django guarda los archivos subidos.
# Aquí se almacenarán los pósters de películas (campo imagen_poster del modelo Pelicula),
# tickets PDF/QR generados y cualquier otro archivo cargado por el administrador.
MEDIA_ROOT = BASE_DIR / 'multimedia'


# ─── CAMPO PRIMARIO POR DEFECTO ───────────────────────────────────────────────

# DEFAULT_AUTO_FIELD: Tipo de campo que Django asigna automáticamente como clave primaria (PK)
# cuando no se define una explícitamente en el modelo.
# BigAutoField = entero de 64 bits autoincremental (soporta hasta 9.2 × 10^18 registros),
# suficiente para el volumen de ventas y tickets del sistema a largo plazo.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── AUTENTICACIÓN ────────────────────────────────────────────────────────────

# AUTH_USER_MODEL: Le indica a Django qué modelo usar como usuario del sistema.
# Por defecto Django usa 'auth.User'. Al apuntar a nuestro modelo 'Usuario',
# todo el sistema de autenticación (login, sesiones, permisos, panel admin)
# trabaja automáticamente con nuestra tabla 'usuario' de la base de datos.
# IMPORTANTE: Esta línea debe estar definida ANTES de correr la primera migración.
# Cambiarla después de migrar requiere resetear la base de datos.
AUTH_USER_MODEL = 'sistema_cine.Usuario'

# LOGIN_URL: URL a la que Django redirige automáticamente cuando un usuario
# intenta acceder a una vista protegida con @login_required sin estar logueado.
LOGIN_URL = '/auth/login/'

# LOGIN_REDIRECT_URL: URL a la que Django redirige después de un login exitoso
# si no había una página de destino previa guardada en sesión.
LOGIN_REDIRECT_URL = '/'

# LOGOUT_REDIRECT_URL: URL a la que Django redirige después de cerrar sesión.
LOGOUT_REDIRECT_URL = '/auth/login/'