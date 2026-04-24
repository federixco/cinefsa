<<<<<<< Updated upstream
# cinefsa
=======
# CineFSA
>>>>>>> Stashed changes

## Dependencias

Las dependencias principales utilizadas en el proyecto hasta ahora son:

- **Django** (Framework web)
- **mysqlclient** (Conector para la base de datos MySQL)
- **python-decouple** (Manejo de variables de entorno y configuración)
- **Pillow** (Procesamiento y manejo de imágenes)

### Instalación

Para instalar todas las dependencias necesarias en un entorno virtual, ejecuta el siguiente comando:

```bash
<<<<<<< Updated upstream
pip install django mysqlclient python-decouple Pillow
```
=======
git clone <URL_DEL_REPOSITORIO>
cd cinefsa
```

### 2. Crear y activar el entorno virtual

Es **OBLIGATORIO** usar un entorno virtual para no tener conflictos de versiones.

En Windows (cmd o PowerShell):
```bash
python -m venv venv
.\venv\Scripts\activate
```

*(Sabrás que está activo cuando veas `(venv)` al inicio de tu línea de comandos).*

### 3. Instalar las dependencias

Con el entorno virtual activado, ejecuta:

```bash
pip install django==4.2.30 mysqlclient python-decouple Pillow
```

### 4. Inicializar la Base de Datos

1. Abre **XAMPP Control Panel** e inicia el módulo **MySQL** (espera a que se ponga en verde).
2. Asegúrate de tener el entorno virtual activado.
3. Ejecuta nuestro script automático que crea la base de datos y aplica las migraciones:

```bash
python iniciar_bd.py
```

### 5. Levantar el Servidor de Desarrollo

Una vez creada la base de datos, inicia el servidor de Django:

```bash
python manage.py runserver
```

Abre tu navegador y ve a: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📁 Estructura del Proyecto

El proyecto sigue una estructura personalizada y en español:

- `configuracion/`: Configuraciones globales de Django (`settings`, `urls`, `wsgi`).
- `sistema_cine/`: App principal de Django (actúa como puente técnico).
- `modelos/`: Contiene la lógica de datos dividida por módulos (`contenido/`, `sala/`, `funcion/`).
- `vistas/`: Lógica de negocio y controladores de peticiones HTTP.
- `formularios/`: Clases para validación de datos.
- `plantillas/`: Archivos HTML.
- `estaticos/`: CSS, JS e imágenes estáticas.
- `multimedia/`: Archivos subidos por los usuarios (pósters, etc.).

Para más detalles sobre cómo crear nuevos módulos o vistas, consultar `GUIA_INICIO_RAPIDO.txt`.
>>>>>>> Stashed changes
