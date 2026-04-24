/**
 * editor_sala.js
 * ==============
 * Lógica interactiva para la grilla del Editor Dinámico de Salas (RF-A01).
 *
 * PROPÓSITO:
 *   Este módulo controla toda la interacción del usuario con el editor visual
 *   de butacas. Permite "pintar" asientos sobre una grilla 2D, redimensionarla,
 *   limpiarla, ver estadísticas en tiempo real y guardar el layout resultante
 *   en la base de datos a través de una petición AJAX (Fetch API + JSON).
 *
 * FLUJO GENERAL:
 *   1. Al cargar la página (DOMContentLoaded), se ejecuta init().
 *   2. init() configura los event listeners y carga el layout existente
 *      (si la sala ya fue diseñada antes) o genera una grilla vacía.
 *   3. El usuario selecciona un "pincel" (general, vip, discapacitado, pasillo)
 *      y hace clic o arrastra sobre las celdas de la grilla para pintarlas.
 *   4. Al hacer clic en "Guardar Layout", se recolecta la información de cada
 *      celda, se construye un JSON y se envía al backend Django via POST AJAX.
 *
 * VARIABLES GLOBALES INYECTADAS DESDE EL TEMPLATE (editor_sala.html):
 *   - SALA_ID (Number):          ID de la sala que se está editando.
 *   - CAPACIDAD_MAXIMA (Number): Capacidad máxima declarada de la sala.
 *   - LAYOUT_GUARDADO (Object|null): JSON con el layout previamente guardado,
 *     o null si la sala no tiene layout configurado aún. Contiene:
 *       { filas: Number, columnas: Number, asientos: Array<{fila, columna, tipo}> }
 */

document.addEventListener('DOMContentLoaded', () => {

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 1: REFERENCIAS AL DOM
    // Se capturan todos los elementos HTML que el script necesita manipular.
    // Se guardan en constantes porque estos elementos nunca cambian de identidad.
    // ═══════════════════════════════════════════════════════════════════════════

    // Contenedor principal de la grilla donde se inyectan dinámicamente las celdas (<div>).
    // Actúa como un CSS Grid cuyo template-columns se ajusta según la cantidad de columnas.
    const gridContainer = document.getElementById('grilla-asientos');

    // Botón que dispara la función de redimensionar la grilla (cambia filas x columnas).
    const btnRedimensionar = document.getElementById('btn-redimensionar');

    // Inputs numéricos donde el usuario define las dimensiones deseadas de la grilla.
    const inputFilas = document.getElementById('input-filas');
    const inputColumnas = document.getElementById('input-columnas');

    // Botón "Limpiar Grilla": resetea todas las celdas a tipo 'pasillo' (vacío).
    const btnLimpiar = document.getElementById('btn-limpiar');

    // Botón "Seleccionar Todo": rellena TODAS las celdas con el pincel actualmente seleccionado.
    // A diferencia de "Limpiar" (que siempre aplica 'pasillo'), este botón aplica el tipo
    // del pincel activo (general, vip, discapacitado o pasillo).
    const btnSeleccionarTodo = document.getElementById('btn-seleccionar-todo');

    // Botón "Guardar Layout": dispara la petición AJAX para persistir el diseño en la BD.
    const btnGuardar = document.getElementById('btn-guardar');

    // Radio buttons del panel de herramientas (sidebar).
    // Cada uno corresponde a un tipo de pincel: 'general', 'vip', 'discapacitado', 'pasillo'.
    // Se seleccionan todos con querySelectorAll porque hay 4 radios con name="pincel".
    const radiosPincel = document.querySelectorAll('input[name="pincel"]');
    
    // ── Elementos de estadísticas (sidebar) ──
    // Spans que muestran los contadores numéricos de cada tipo de asiento.
    // Se actualizan en tiempo real cada vez que el usuario pinta o borra una celda.
    const statGeneral = document.getElementById('stat-general');
    const statVip = document.getElementById('stat-vip');
    const statDiscapacitado = document.getElementById('stat-discapacitado');
    const statTotal = document.getElementById('stat-total');

    // Alerta de capacidad (actualmente no se usa activamente, pero está preparada
    // para mostrar un mensaje si se excede la capacidad máxima de la sala).
    const alertaCapacidad = document.getElementById('alerta-capacidad');

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 2: ESTADO INTERNO DEL EDITOR
    // Variables que controlan el comportamiento del editor en memoria.
    // No se persisten hasta que el usuario haga clic en "Guardar Layout".
    // ═══════════════════════════════════════════════════════════════════════════

    // pincelActual: Tipo de asiento que se aplica al hacer clic sobre una celda.
    // Valores posibles: 'general', 'vip', 'discapacitado', 'pasillo'.
    // Se actualiza cuando el usuario cambia la selección en los radio buttons del sidebar.
    let pincelActual = 'general';

    // isDragging: Flag booleano que indica si el usuario mantiene presionado el botón
    // del mouse. Permite "pintar arrastrando" (como un pincel real): si isDragging es true
    // y el mouse pasa sobre una celda (mouseenter), se aplica el pincel automáticamente.
    let isDragging = false;
    
    // filas y columnas: Dimensiones actuales de la matriz de la grilla.
    // Se inicializan en 10x15 por defecto, pero se sobreescriben si existe un layout guardado.
    // Rango válido: 1 a 30 (validado en redimensionarGrilla).
    let filas = 10;
    let columnas = 15;

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 3: INICIALIZACIÓN
    // Función principal que configura todos los event listeners y renderiza
    // la grilla inicial (vacía o con datos guardados).
    // ═══════════════════════════════════════════════════════════════════════════

    function init() {

        // ── 3.1: Configurar cambio de pincel ──
        // Se itera sobre cada radio button y se escucha el evento 'change'.
        // Cuando el usuario selecciona un pincel diferente:
        //   a) Se actualiza pincelActual con el value del radio ('general', 'vip', etc.).
        //   b) Se quita la clase CSS 'active' de todos los botones del toolbar.
        //   c) Se agrega la clase 'active' al <label> padre del radio seleccionado,
        //      generando el efecto visual de "botón presionado" en el sidebar.
        radiosPincel.forEach(radio => {
            radio.addEventListener('change', (e) => {
                pincelActual = e.target.value;
                document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
                e.target.parentElement.classList.add('active');
            });
        });

        // ── 3.2: Configurar sistema de "pintar arrastrando" (drag-paint) ──
        // mousedown en cualquier parte del documento activa isDragging.
        // mouseup en cualquier parte lo desactiva.
        // Esto permite que al arrastrar el mouse sobre la grilla, cada celda
        // que recibe un 'mouseenter' se pinte automáticamente con el pincel actual.
        document.addEventListener('mousedown', () => isDragging = true);
        document.addEventListener('mouseup', () => isDragging = false);

        // Se previene el comportamiento nativo de "drag" del navegador sobre la grilla,
        // que intentaría arrastrar los elementos como si fueran imágenes o texto seleccionable.
        gridContainer.addEventListener('dragstart', (e) => e.preventDefault());

        // ── 3.3: Configurar eventos de los botones de acción ──
        // Botón "Aplicar" (redimensionar): valida y reconstruye la grilla con nuevas dimensiones.
        btnRedimensionar.addEventListener('click', redimensionarGrilla);

        // Botón "Limpiar Grilla": rellena TODAS las celdas con tipo 'pasillo' (vacío).
        // Equivale a un "borrar todo" sin cambiar las dimensiones de la grilla.
        btnLimpiar.addEventListener('click', () => llenarGrilla('pasillo'));

        // Botón "Seleccionar Todo": rellena toda la grilla con el pincel actual.
        // Usa la misma función llenarGrilla() pero con pincelActual en vez de 'pasillo'.
        btnSeleccionarTodo.addEventListener('click', () => llenarGrilla(pincelActual));

        // Botón "Guardar Layout": inicia el proceso asíncrono de guardado via AJAX.
        btnGuardar.addEventListener('click', guardarLayout);

        // ── 3.4: Cargar layout existente o crear grilla vacía ──
        // LAYOUT_GUARDADO es una variable global inyectada desde el template Django.
        // Si la sala ya tiene un layout guardado (no es null y tiene filas/columnas),
        // se restauran las dimensiones y se renderiza la grilla con los asientos guardados.
        // Si no tiene layout, se crea una grilla vacía de 10x15 (todo 'pasillo').
        if (LAYOUT_GUARDADO && LAYOUT_GUARDADO.filas && LAYOUT_GUARDADO.columnas) {
            filas = LAYOUT_GUARDADO.filas;
            columnas = LAYOUT_GUARDADO.columnas;
            inputFilas.value = filas;
            inputColumnas.value = columnas;
            renderizarGrilla(LAYOUT_GUARDADO.asientos);
        } else {
            renderizarGrilla();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 4: RENDERIZADO Y LÓGICA DE LA GRILLA
    // Funciones que construyen, modifican y manipulan las celdas de la grilla.
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * redimensionarGrilla()
     * Lee los valores de los inputs de filas/columnas, valida que estén en rango
     * (1-30), pide confirmación al usuario (ya que se pierde el diseño no guardado)
     * y reconstruye la grilla con las nuevas dimensiones.
     */
    function redimensionarGrilla() {
        const newFilas = parseInt(inputFilas.value);
        const newColumnas = parseInt(inputColumnas.value);

        // Validación: las dimensiones deben estar entre 1 y 30.
        // 30x30 = 900 celdas máximo, un límite razonable para el rendimiento del DOM.
        if (newFilas < 1 || newFilas > 30 || newColumnas < 1 || newColumnas > 30) {
            alert('Las dimensiones deben estar entre 1 y 30.');
            return;
        }

        // Confirmación del usuario: redimensionar destruye el layout actual no guardado.
        if (confirm('¿Seguro que deseas redimensionar? Se perderá el layout actual no guardado.')) {
            filas = newFilas;
            columnas = newColumnas;
            renderizarGrilla();
        }
    }

    /**
     * renderizarGrilla(matrizGuardada)
     * Construye toda la grilla de asientos en el DOM.
     *
     * @param {Array|null} matrizGuardada - Array de objetos {fila, columna, tipo} del layout
     *   guardado previamente. Si es null, todas las celdas se inicializan como 'pasillo'.
     *
     * PROCESO:
     *   1. Limpia el HTML del contenedor de la grilla.
     *   2. Ajusta el CSS grid-template-columns según la cantidad de columnas.
     *   3. Itera fila por fila, columna por columna, creando un <div> por cada celda.
     *   4. Si hay datos guardados, busca la celda correspondiente y aplica su tipo.
     *   5. Registra eventos mousedown/mouseenter en cada celda para el sistema de pintado.
     *   6. Actualiza las estadísticas del sidebar.
     */
    function renderizarGrilla(matrizGuardada = null) {
        // Vaciar el contenido previo de la grilla para reconstruirla desde cero.
        gridContainer.innerHTML = '';

        // Definir las columnas del CSS Grid dinámicamente.
        // Cada columna tiene 32px de ancho (coincide con el tamaño de .seat en CSS).
        gridContainer.style.gridTemplateColumns = `repeat(${columnas}, 32px)`;

        // Doble bucle para crear la matriz: fila externa, columna interna.
        // Las posiciones empiezan en 1 (no en 0) para coincidir con la lógica del backend.
        for (let f = 1; f <= filas; f++) {
            for (let c = 1; c <= columnas; c++) {
                // Crear el elemento <div> que representa una celda/butaca.
                const seat = document.createElement('div');
                seat.classList.add('seat');
                
                // Almacenar la posición de la celda en data-attributes.
                // Estos valores se leen luego al guardar para construir el JSON.
                seat.dataset.fila = f;
                seat.dataset.columna = c;

                // Determinar el tipo inicial de la celda.
                // Por defecto es 'pasillo' (vacío). Si hay datos guardados,
                // se busca en el array si existe un asiento en esta posición (fila, columna).
                let tipo = 'pasillo';
                if (matrizGuardada) {
                    // .find() busca el primer elemento que coincida con fila Y columna.
                    // Complejidad O(n) por cada celda — aceptable para grillas pequeñas (≤900 celdas).
                    const savedSeat = matrizGuardada.find(s => s.fila === f && s.columna === c);
                    if (savedSeat) tipo = savedSeat.tipo;
                }
                
                // Aplicar la clase CSS y contenido visual correspondiente al tipo.
                aplicarTipoAsiento(seat, tipo);

                // ── Eventos de interacción para el sistema de pintado ──
                // mousedown: Al hacer clic sobre la celda, aplicar el pincel actual.
                seat.addEventListener('mousedown', () => aplicarPincel(seat));

                // mouseenter: Al pasar el mouse sobre la celda MIENTRAS se arrastra
                // (isDragging === true), aplicar el pincel. Esto crea el efecto de
                // "pintar arrastrando" como en un editor de imágenes.
                seat.addEventListener('mouseenter', () => {
                    if (isDragging) aplicarPincel(seat);
                });

                // Agregar la celda al contenedor de la grilla en el DOM.
                gridContainer.appendChild(seat);
            }
        }
        
        // Recalcular y mostrar las estadísticas después de renderizar.
        actualizarEstadisticas();
    }

    /**
     * llenarGrilla(tipo)
     * Aplica un mismo tipo a TODAS las celdas de la grilla.
     * Se usa principalmente para "Limpiar Grilla" (tipo='pasillo').
     *
     * @param {string} tipo - Tipo de asiento a aplicar: 'general', 'vip', 'discapacitado' o 'pasillo'.
     */
    function llenarGrilla(tipo) {
        document.querySelectorAll('.seat').forEach(seat => {
            aplicarTipoAsiento(seat, tipo);
        });
        actualizarEstadisticas();
    }

    /**
     * aplicarPincel(seatElement)
     * Aplica el pincel actualmente seleccionado a una celda específica.
     * Es el intermediario entre los eventos del mouse y aplicarTipoAsiento().
     *
     * @param {HTMLElement} seatElement - El <div> de la celda sobre la que se hizo clic/arrastró.
     */
    function aplicarPincel(seatElement) {
        aplicarTipoAsiento(seatElement, pincelActual);
        actualizarEstadisticas();
    }

    /**
     * aplicarTipoAsiento(seatElement, tipo)
     * Función nuclear del editor: aplica un tipo de asiento a una celda del DOM.
     * Actualiza las clases CSS (para el color visual) y el data-attribute (para la lógica).
     *
     * @param {HTMLElement} seatElement - El <div> de la celda a modificar.
     * @param {string} tipo - El tipo a aplicar: 'general', 'vip', 'discapacitado' o 'pasillo'.
     *
     * PROCESO:
     *   1. Remueve todas las clases de tipo previas para evitar conflictos visuales.
     *   2. Agrega la nueva clase CSS que corresponde al tipo (define el color de fondo).
     *   3. Actualiza el data-attribute 'tipo' para uso en la lógica de guardado.
     *   4. Limpia el contenido interno y agrega íconos especiales si corresponde:
     *      - VIP: estrella (★)
     *      - Discapacitado: símbolo de accesibilidad (♿)
     */
    function aplicarTipoAsiento(seatElement, tipo) {
        seatElement.classList.remove('pasillo', 'general', 'vip', 'discapacitado');
        seatElement.classList.add(tipo);
        seatElement.dataset.tipo = tipo;

        seatElement.innerHTML = '';
        if (tipo === 'vip') seatElement.innerHTML = '★';
        if (tipo === 'discapacitado') seatElement.innerHTML = '♿';
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 5: ESTADÍSTICAS EN TIEMPO REAL
    // Recuenta los asientos por tipo y actualiza los contadores del sidebar.
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * actualizarEstadisticas()
     * Recorre todas las celdas de la grilla, cuenta cuántas hay de cada tipo
     * (general, vip, discapacitado) y actualiza los spans del sidebar con los totales.
     * Se ejecuta cada vez que se pinta, borra o reconstruye la grilla.
     *
     * @returns {boolean} true — actualmente retorna siempre true (preparado para
     *   futuras validaciones que podrían retornar false si se excede la capacidad).
     */
    function actualizarEstadisticas() {
        const seats = document.querySelectorAll('.seat');
        
        // Contadores inicializados en 0 para cada tipo de asiento.
        let countGeneral = 0;
        let countVip = 0;
        let countDiscapacitado = 0;

        // Recorrer TODAS las celdas y clasificarlas según su data-attribute 'tipo'.
        // Las celdas tipo 'pasillo' no se cuentan (son espacios vacíos).
        seats.forEach(seat => {
            const tipo = seat.dataset.tipo;
            if (tipo === 'general') countGeneral++;
            else if (tipo === 'vip') countVip++;
            else if (tipo === 'discapacitado') countDiscapacitado++;
        });

        // Total de butacas asignadas (excluyendo pasillos).
        // Este valor se usará como capacidad_maxima de la sala al guardar.
        const totalAsignadas = countGeneral + countVip + countDiscapacitado;

        // Actualizar los textos de los contadores en el sidebar del editor.
        statGeneral.textContent = countGeneral;
        statVip.textContent = countVip;
        statDiscapacitado.textContent = countDiscapacitado;
        statTotal.textContent = totalAsignadas;

        return true;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // SECCIÓN 6: GUARDADO ASÍNCRONO (AJAX CON FETCH API)
    // Envía el layout diseñado al backend Django para persistirlo en MySQL.
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * guardarLayout()
     * Función asíncrona que recolecta el estado de toda la grilla, construye un JSON
     * con la información y lo envía al endpoint Django via POST.
     *
     * FLUJO:
     *   1. Deshabilita el botón para evitar doble clic (UX).
     *   2. Recorre todas las celdas y filtra solo las que NO son 'pasillo'.
     *   3. Construye el objeto JSON con: { filas, columnas, asientos[] }.
     *   4. Obtiene el token CSRF de Django (necesario para POST seguros).
     *   5. Envía el POST via Fetch API al endpoint /panel/salas/<id>/guardar-layout/.
     *   6. Maneja la respuesta (éxito o error) con alertas al usuario.
     *   7. Restaura el botón al estado original en el bloque finally.
     *
     * ENDPOINT BACKEND: guardar_layout() en vistas/editor_sala.py
     *   - Recibe el JSON.
     *   - Actualiza la capacidad_maxima de la sala.
     *   - Guarda el JSON crudo en sala.layout_config.
     *   - Sincroniza los asientos individuales en la tabla 'asiento' de la BD.
     */
    async function guardarLayout() {

        // Deshabilitar el botón y cambiar su texto para dar feedback visual al usuario.
        // Evita que el usuario haga clic múltiples veces mientras se procesa la petición.
        btnGuardar.disabled = true;
        btnGuardar.textContent = 'Guardando...';

        try {
            // ── Paso 1: Recolectar datos de la grilla ──
            // Se seleccionan TODOS los <div class="seat"> del DOM.
            const seatsElements = document.querySelectorAll('.seat');
            const asientosData = [];

            // Iterar sobre cada celda y extraer solo las que son asientos reales.
            // Las celdas tipo 'pasillo' se ignoran: representan espacios vacíos
            // y no se persisten en la base de datos.
            seatsElements.forEach(seat => {
                const tipo = seat.dataset.tipo;
                if (tipo !== 'pasillo') {
                    asientosData.push({
                        fila: parseInt(seat.dataset.fila),       // Posición vertical (1-indexed)
                        columna: parseInt(seat.dataset.columna), // Posición horizontal (1-indexed)
                        tipo: tipo                                // 'general', 'vip' o 'discapacitado'
                    });
                }
            });

            // ── Paso 2: Construir el objeto JSON completo ──
            // Este objeto se guarda tal cual en sala.layout_config (JSONField de Django)
            // para poder reconstruir la grilla la próxima vez que se abra el editor.
            const layoutData = {
                filas: filas,           // Cantidad de filas de la grilla
                columnas: columnas,     // Cantidad de columnas de la grilla
                asientos: asientosData  // Array de asientos (sin pasillos)
            };

            // ── Paso 3: Obtener el token CSRF de Django ──
            // Django requiere un token CSRF en toda petición POST para prevenir ataques
            // de Cross-Site Request Forgery. El token fue inyectado en el HTML por el
            // template tag {% csrf_token %} como un <input type="hidden">.
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // ── Paso 4: Enviar la petición POST via Fetch API ──
            // Se usa Fetch API (nativa del navegador) en lugar de XMLHttpRequest
            // por ser más moderna, legible y compatible con async/await.
            const response = await fetch(`/panel/salas/${SALA_ID}/guardar-layout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',  // Indicar que el body es JSON
                    'X-CSRFToken': csrfToken              // Header requerido por Django CSRF
                },
                body: JSON.stringify(layoutData) // Serializar el objeto a string JSON
            });

            // ── Paso 5: Procesar la respuesta del servidor ──
            const data = await response.json();

            if (response.ok) {
                // HTTP 200: El backend procesó correctamente el layout.
                alert('Layout guardado correctamente. Se crearon/actualizaron los asientos en la Base de Datos.');
            } else {
                // HTTP 4xx/5xx: Hubo un error en el backend.
                alert('Error al guardar: ' + (data.error || 'Error desconocido'));
            }

        } catch (error) {
            // Error de red (sin conexión, servidor caído, etc.).
            console.error('Error de red:', error);
            alert('Error de conexión con el servidor.');
        } finally {
            // ── Paso 6: Restaurar el botón siempre (éxito o error) ──
            // El bloque finally se ejecuta sin importar si hubo excepción o no.
            btnGuardar.disabled = false;
            btnGuardar.textContent = 'Guardar Layout';
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // PUNTO DE ENTRADA: Ejecutar la inicialización del editor.
    // ═══════════════════════════════════════════════════════════════════════════
    init();
});
