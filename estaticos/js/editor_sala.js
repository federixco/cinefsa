/**
 * editor_sala.js
 * Lógica interactiva para la grilla del Editor Dinámico de Salas.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ─── REFERENCIAS AL DOM ──────────────────────────────────────────────────
    const gridContainer = document.getElementById('grilla-asientos');
    const btnRedimensionar = document.getElementById('btn-redimensionar');
    const inputFilas = document.getElementById('input-filas');
    const inputColumnas = document.getElementById('input-columnas');
    const btnLimpiar = document.getElementById('btn-limpiar');
    const btnGuardar = document.getElementById('btn-guardar');
    const radiosPincel = document.querySelectorAll('input[name="pincel"]');
    
    // Contadores
    const statGeneral = document.getElementById('stat-general');
    const statVip = document.getElementById('stat-vip');
    const statDiscapacitado = document.getElementById('stat-discapacitado');
    const statTotal = document.getElementById('stat-total');
    const alertaCapacidad = document.getElementById('alerta-capacidad');

    // ─── ESTADO INTERNO ──────────────────────────────────────────────────────
    // pincelActual puede ser: 'general', 'vip', 'discapacitado', 'pasillo'
    let pincelActual = 'general';
    let isDragging = false; // Para pintar arrastrando el mouse
    
    // Dimensiones actuales de la matriz
    let filas = 10;
    let columnas = 15;

    // ─── INICIALIZACIÓN ──────────────────────────────────────────────────────
    function init() {
        // Configurar pincel seleccionado
        radiosPincel.forEach(radio => {
            radio.addEventListener('change', (e) => {
                pincelActual = e.target.value;
                // Actualizar estilos visuales de los botones
                document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
                e.target.parentElement.classList.add('active');
            });
        });

        // Configurar eventos globales de drag
        document.addEventListener('mousedown', () => isDragging = true);
        document.addEventListener('mouseup', () => isDragging = false);
        // Prevenir comportamiento default al arrastrar para que no seleccione texto
        gridContainer.addEventListener('dragstart', (e) => e.preventDefault());

        // Eventos de botones
        btnRedimensionar.addEventListener('click', redimensionarGrilla);
        btnLimpiar.addEventListener('click', () => llenarGrilla('pasillo'));
        btnGuardar.addEventListener('click', guardarLayout);

        // Cargar layout existente o crear grilla vacia
        if (LAYOUT_GUARDADO && LAYOUT_GUARDADO.filas && LAYOUT_GUARDADO.columnas) {
            filas = LAYOUT_GUARDADO.filas;
            columnas = LAYOUT_GUARDADO.columnas;
            inputFilas.value = filas;
            inputColumnas.value = columnas;
            renderizarGrilla(LAYOUT_GUARDADO.asientos);
        } else {
            // Estado por defecto: todo "pasillo" (vacío)
            renderizarGrilla();
        }
    }

    // ─── RENDERIZADO Y LÓGICA DE LA GRILLA ───────────────────────────────────
    function redimensionarGrilla() {
        const newFilas = parseInt(inputFilas.value);
        const newColumnas = parseInt(inputColumnas.value);

        if (newFilas < 1 || newFilas > 30 || newColumnas < 1 || newColumnas > 30) {
            alert('Las dimensiones deben estar entre 1 y 30.');
            return;
        }

        if (confirm('¿Seguro que deseas redimensionar? Se perderá el layout actual no guardado.')) {
            filas = newFilas;
            columnas = newColumnas;
            renderizarGrilla();
        }
    }

    function renderizarGrilla(matrizGuardada = null) {
        gridContainer.innerHTML = ''; // Limpiar grilla actual
        gridContainer.style.gridTemplateColumns = `repeat(${columnas}, 32px)`;

        for (let f = 1; f <= filas; f++) {
            for (let c = 1; c <= columnas; c++) {
                const seat = document.createElement('div');
                seat.classList.add('seat');
                
                // Asignar ID para identificar posición: Fila_Columna
                seat.dataset.fila = f;
                seat.dataset.columna = c;

                // Determinar estado inicial
                let tipo = 'pasillo';
                if (matrizGuardada) {
                    const savedSeat = matrizGuardada.find(s => s.fila === f && s.columna === c);
                    if (savedSeat) tipo = savedSeat.tipo;
                }
                
                aplicarTipoAsiento(seat, tipo);

                // Eventos de interacción
                seat.addEventListener('mousedown', () => aplicarPincel(seat));
                seat.addEventListener('mouseenter', () => {
                    if (isDragging) aplicarPincel(seat);
                });

                gridContainer.appendChild(seat);
            }
        }
        
        actualizarEstadisticas();
    }

    function llenarGrilla(tipo) {
        document.querySelectorAll('.seat').forEach(seat => {
            aplicarTipoAsiento(seat, tipo);
        });
        actualizarEstadisticas();
    }

    function aplicarPincel(seatElement) {
        aplicarTipoAsiento(seatElement, pincelActual);
        actualizarEstadisticas();
    }

    function aplicarTipoAsiento(seatElement, tipo) {
        // Limpiar clases anteriores
        seatElement.classList.remove('pasillo', 'general', 'vip', 'discapacitado');
        
        // Aplicar nueva clase
        seatElement.classList.add(tipo);
        seatElement.dataset.tipo = tipo;

        // Limpiar contenido (texto/icono)
        seatElement.innerHTML = '';
        if (tipo === 'vip') seatElement.innerHTML = '★';
        if (tipo === 'discapacitado') seatElement.innerHTML = '♿';
    }

    // ─── ESTADÍSTICAS Y VALIDACIÓN ───────────────────────────────────────────
    function actualizarEstadisticas() {
        const seats = document.querySelectorAll('.seat');
        
        let countGeneral = 0;
        let countVip = 0;
        let countDiscapacitado = 0;

        seats.forEach(seat => {
            const tipo = seat.dataset.tipo;
            if (tipo === 'general') countGeneral++;
            else if (tipo === 'vip') countVip++;
            else if (tipo === 'discapacitado') countDiscapacitado++;
        });

        const totalAsignadas = countGeneral + countVip + countDiscapacitado;

        // Actualizar UI
        statGeneral.textContent = countGeneral;
        statVip.textContent = countVip;
        statDiscapacitado.textContent = countDiscapacitado;
        statTotal.textContent = totalAsignadas;

        return true;
    }

    // ─── GUARDADO (AJAX) ─────────────────────────────────────────────────────
    async function guardarLayout() {

        // Deshabilitar botón para evitar doble click
        btnGuardar.disabled = true;
        btnGuardar.textContent = 'Guardando...';

        try {
            // Construir JSON
            const seatsElements = document.querySelectorAll('.seat');
            const asientosData = [];

            seatsElements.forEach(seat => {
                const tipo = seat.dataset.tipo;
                if (tipo !== 'pasillo') { // No guardamos los pasillos en la BD, solo los asientos reales
                    asientosData.push({
                        fila: parseInt(seat.dataset.fila),
                        columna: parseInt(seat.dataset.columna),
                        tipo: tipo
                    });
                }
            });

            const layoutData = {
                filas: filas,
                columnas: columnas,
                asientos: asientosData
            };

            // Obtener CSRF Token de Django (inyectado en el template HTML)
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Enviar POST via Fetch API
            const response = await fetch(`/panel/salas/${SALA_ID}/guardar-layout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(layoutData)
            });

            const data = await response.json();

            if (response.ok) {
                alert('Layout guardado correctamente. Se crearon/actualizaron los asientos en la Base de Datos.');
            } else {
                alert('Error al guardar: ' + (data.error || 'Error desconocido'));
            }

        } catch (error) {
            console.error('Error de red:', error);
            alert('Error de conexión con el servidor.');
        } finally {
            // Restaurar botón
            btnGuardar.disabled = false;
            btnGuardar.textContent = 'Guardar Layout';
        }
    }

    // Arrancar la logica
    init();
});
