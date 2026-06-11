## Sistema Web de Gestión Cinematográfica

<div align="center">

**Plataforma integral para la administración y venta de entradas de un complejo de cines.**

Desarrollado con **Django 4.2 LTS** · **MySQL/MariaDB** · **Mercado Pago** · **Python 3.10+**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2_LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![MercadoPago](https://img.shields.io/badge/Mercado_Pago-Checkout_Pro-009EE3?style=for-the-badge&logo=mercadopago&logoColor=white)](https://www.mercadopago.com.ar/developers)

</div>

---

## Descripción

Es un sistema web completo que permite gestionar todas las operaciones de un complejo de cines:
desde la cartelera de películas y la venta de entradas con pasarela de pago, hasta un editor visual de salas
y un módulo de votación comunitaria (Cine Club). Incluye herramientas de desarrollo como un monitor SQL
en tiempo real y la integración con Django Debug Toolbar para análisis de consultas.

---

## Funcionalidades Principales

### Portal Público (Clientes)

| Módulo | Descripción |
|---|---|
| **Cartelera Inteligente** | Muestra las películas con funciones en los próximos 7 días, filtro por género, y cálculo de asientos disponibles mediante la función nativa `fn_asientos_disponibles()` de MySQL |
| **Compra de Entradas** | Selección visual e interactiva de asientos sobre el mapa de la sala, integración con Mercado Pago Checkout Pro y generación automática de tickets con código QR |
| **Cine Club — Votación** | Portal de votación para películas clásicas. Los clientes registrados eligen qué película quieren ver en eventos especiales. Soporte para múltiples encuestas activas simultáneamente |
| **Historial de Compras** | Cada usuario puede consultar su historial de ventas y descargar sus tickets QR |
| **Autenticación** | Registro, inicio de sesión por email, cierre de sesión y cambio de contraseña |

### Panel de Administración

| Módulo | Descripción |
|---|---|
| **Editor Visual de Salas** | Editor drag-and-drop con grilla interactiva para diseñar la disposición de asientos (general, VIP, discapacitado). El layout se persiste en JSON y sincroniza los registros de asientos automáticamente con soft-delete inteligente |
| **Gestión de Cartelera** | ABM completo de Géneros, Películas y Funciones. Validación automática de solapamiento de horarios en la misma sala |
| **Gestión de Usuarios** | Búsqueda y filtrado de usuarios por nombre, email o rol. Asignación y revocación del rol de Empleado con generación automática de ID de validador vía procedimiento almacenado |
| **Monitor de Votaciones** | Dashboard con todas las encuestas, estadísticas en tiempo real, barras de progreso con porcentajes y ganador destacado |
| **Validador QR de Tickets** | Escáner de cámara para que los empleados validen tickets en la entrada. Controla ventana horaria (30 min antes a 15 min después de la función) y detecta tickets ya utilizados |

### Seguridad y Concurrencia

| Mecanismo | Descripción |
|---|---|
| **Restricción `unique_together`** | Evita la venta duplicada del mismo asiento para la misma función a nivel motor de base de datos |
| **`SELECT FOR UPDATE`** | Bloqueo pesimista dentro de transacciones atómicas al momento de confirmar la compra |
| **Roles con Decoradores** | `@solo_empleado` y `@solo_administrador` para control de acceso granular a vistas sensibles |
| **Trigger de Mantenimiento** | Trigger `BEFORE INSERT` en tickets que impide la venta si la sala está en mantenimiento (`SIGNAL SQLSTATE '45000'`) |

---

## Arquitectura del Sistema

```
sistema/
│
├── configuracion/          # Configuración global de Django (settings, urls, wsgi)
├── sistema_cine/           # App principal (puente técnico para modelos y migraciones)
│
├── modelos/                # Capa de datos — Modelos organizados por dominio
│   ├── identidad/          #   → Usuario, Cliente, Empleado, Administrador
│   ├── contenido/          #   → Género, Película
│   ├── sala/               #   → Sala, Asiento
│   ├── funcion/            #   → Función (proyección)
│   ├── ventas/             #   → Venta, Ticket
│   └── votacion/           #   → Encuesta, Voto
│
├── vistas/                 # Capa de lógica — Controladores HTTP
│   ├── autenticacion/      #   → Login, Registro, Logout, Historial
│   ├── compras/            #   → Selección de asientos, Pago MP, Tickets QR
│   ├── panel/              #   → 27 rutas del panel administrativo
│   ├── portal.py           #   → Página principal / Cartelera
│   ├── votacion.py         #   → Cine Club / Votaciones
│   └── decoradores.py      #   → Control de acceso por roles
│
├── formularios/            # Validación de datos de entrada
│   ├── autenticacion.py    #   → Registro e inicio de sesión
│   ├── cartelera.py        #   → Géneros, Películas, Funciones
│   ├── usuarios.py         #   → Búsqueda y asignación de empleados
│   └── votaciones.py       #   → Creación de encuestas
│
├── servicios/              # Capa de servicios externos
│   ├── mercadopago_service.py  # → Integración con Mercado Pago
│   ├── compra_service.py       # → Lógica transaccional de compras
│   └── qr_service.py           # → Generación de códigos QR
│
├── plantillas/             # Templates HTML (18 archivos)
│   ├── base/               #   → Layouts principales (portal + panel)
│   ├── autenticacion/      #   → Login, Registro, Historial, Cambio de contraseña
│   ├── portal/             #   → Inicio, Cine Club, Selección asientos, Tickets
│   └── panel/              #   → Todas las vistas del panel admin
│
├── estaticos/              # Archivos estáticos
│   ├── css/                #   → 6 hojas de estilo
│   └── js/                 #   → Editor de salas, Panel de usuarios
│
├── sql/                    # Scripts SQL nativos
│   └── triggers_y_procedimientos.sql
│
├── multimedia/             # Archivos subidos (pósters, tickets QR)
│
├── monitor_sql.py          # 🔍 Monitor GUI de consultas SQL en tiempo real
├── launcher.py             # 🚀 Lanzador GUI del sistema (MySQL + Django)
├── iniciar_bd.py           # 🗄️ Script de inicialización de base de datos
└── setup_inicial.py        # 🌱 Seeder de datos iniciales (admin + géneros)
```

---

## Base de Datos — Objetos Nativos SQL

El sistema aprovecha las capacidades nativas de MySQL mediante triggers, funciones y procedimientos almacenados:

| Objeto | Tipo | Descripción |
|---|---|---|
| `trg_asiento_after_insert` | Trigger | Recalcula `capacidad_maxima` de la sala al agregar asientos |
| `trg_asiento_after_delete` | Trigger | Recalcula capacidad al eliminar asientos |
| `trg_asiento_after_update` | Trigger | Recalcula capacidad al cambiar el estado de un asiento (soft-delete) |
| `trg_ticket_check_mantenimiento` | Trigger | Impide la venta de tickets si la sala está en mantenimiento |
| `sp_generar_id_validador` | Procedimiento | Genera automáticamente el siguiente ID correlativo de validador (`emp-001`, `emp-002`, ...) |
| `fn_asientos_disponibles` | Función | Calcula los asientos disponibles para una función: `(activos en sala) - (tickets vendidos)` |

---

##  Requisitos Previos

- **Python 3.10+** — [Descargar](https://www.python.org/downloads/)
- **XAMPP** con MySQL/MariaDB 10.4+ — [Descargar](https://www.apachefriends.org/es/index.html)
- **Git** — [Descargar](https://git-scm.com/)

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/cinefsa.git
cd cinefsa
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
copy .env.example .env
```

Editá el archivo `.env` y reemplazá el valor de `MERCADOPAGO_ACCESS_TOKEN` con tu Access Token de la [consola de desarrolladores de Mercado Pago](https://www.mercadopago.com.ar/developers/panel/app).

### 5. Inicializar la base de datos

Asegurate de que **MySQL esté corriendo** (iniciá XAMPP y prendé el módulo MySQL).

```bash
python iniciar_bd.py
```

Este script crea la base de datos `sistema_cine`, ejecuta las migraciones y deja todo listo.

### 6. Cargar datos iniciales

```bash
python setup_inicial.py
```

Crea el usuario administrador por defecto y los 15 géneros cinematográficos.

> **Credenciales del administrador:**
> - Email: `admin@cinefsa.com`
> - Contraseña: `admin1234`

### 7. Levantar el servidor

```bash
python manage.py runserver
```

Abrí tu navegador en **http://127.0.0.1:8000/**

---

##  Herramientas de Desarrollo

### Launcher GUI

El proyecto incluye un lanzador gráfico de escritorio que permite controlar MySQL y Django desde una sola ventana:

```bash
python launcher.py
```

### Monitor SQL en Tiempo Real

Herramienta gráfica que muestra todas las consultas SQL formateadas, coloreadas por tipo de operación e indentadas automáticamente con `sqlparse`:

```bash
python monitor_sql.py
```

| Color | Operación |
|---|---|
| 🟢 Verde | `INSERT` |
| 🔵 Cian | `SELECT` |
| 🟡 Amarillo | `UPDATE` / `DELETE` |
| 🟣 Magenta | `BEGIN` / `COMMIT` / `SET` |

### Django Debug Toolbar

Disponible automáticamente en el navegador al acceder a cualquier página. Permite inspeccionar consultas SQL, tiempos de respuesta, templates renderizados y más.

---

## Dependencias

| Paquete | Versión | Uso |
|---|---|---|
| `Django` | 4.2.30 | Framework web principal |
| `mysqlclient` | 2.2.8 | Conector nativo para MySQL/MariaDB |
| `python-decouple` | 3.8 | Manejo seguro de variables de entorno |
| `Pillow` | 12.2.0 | Procesamiento de imágenes (pósters) |
| `mercadopago` | ≥3.1 | SDK de Mercado Pago para pagos online |
| `qrcode` | ≥8.2 | Generación de códigos QR para tickets |
| `sqlparse` | 0.5.5 | Formateo e indentación de consultas SQL |
| `django-debug-toolbar` | ≥6.3.0 | Herramienta de depuración en navegador |

---

## Mapa de Rutas

| Ruta | Descripción | Acceso |
|---|---|---|
| `/` | Cartelera principal | Público |
| `/auth/login/` | Inicio de sesión | Público |
| `/auth/registro/` | Registro de cuenta | Público |
| `/auth/historial/` | Historial de compras | Cliente autenticado |
| `/auth/cambiar-password/` | Cambio de contraseña | Usuario autenticado |
| `/cine-club/` | Portal de votación | Público (votar requiere cuenta) |
| `/compras/funcion/<id>/asientos/` | Selección de asientos | Cliente autenticado |
| `/compras/verificar-pago/` | Verificación de pago MP | Cliente autenticado |
| `/panel/` | Panel de administración | Empleado / Administrador |
| `/panel/salas/` | Gestión de salas | Administrador |
| `/panel/salas/<id>/editor/` | Editor visual de sala | Administrador |
| `/panel/peliculas/` | Gestión de películas | Administrador |
| `/panel/funciones/` | Gestión de funciones | Administrador |
| `/panel/usuarios/` | Gestión de usuarios | Administrador |
| `/panel/votaciones/` | Monitor de votaciones | Administrador |
| `/panel/scanner-qr/` | Validador QR de tickets | Empleado |

---

## Roles del Sistema

```
                    ┌──────────────┐
                    │   Usuario    │  ← Supertipo (login por email)
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌────────────┐ ┌────────────┐ ┌───────────────┐
     │  Cliente   │ │  Empleado  │ │ Administrador │
     └────────────┘ └────────────┘ └───────────────┘
     • Comprar      • Vender en     • Gestionar salas
       entradas       boletería     • ABM cartelera
     • Votar en     • Cobrar en     • Gestionar usuarios
       Cine Club      efectivo      • Crear encuestas
     • Ver historial• Validar QR    • Monitor votaciones
```

---

## Licencia

Este proyecto fue desarrollado como Trabajo Integrador Final para las materias de Base de datos I y Programación III de la carrera Licenciatura en sistemas de información.

