/**
 * panel_usuarios.js — Lógica interactiva del Panel de Gestión de Usuarios (RF-A05).
 *
 * Funcionalidades:
 *   1. Modal de asignación de rol: abrir/cerrar con datos dinámicos del usuario seleccionado.
 *   2. Cierre del modal con Escape o clic fuera.
 */

document.addEventListener('DOMContentLoaded', () => {

    // ═══════════════════════════════════════════════════════════════════════════
    // REFERENCIAS AL DOM
    // ═══════════════════════════════════════════════════════════════════════════

    const modalOverlay = document.getElementById('modal-asignar');
    const modalNombre = document.getElementById('modal-nombre-usuario');
    const modalEmail = document.getElementById('modal-email-usuario');
    const modalInputUsuarioId = document.getElementById('modal-usuario-id');
    const modalInputTerminal = document.getElementById('modal-terminal-venta');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');

    // ═══════════════════════════════════════════════════════════════════════════
    // MODAL: ABRIR
    // Se invoca desde los botones "Asignar" de cada fila de la tabla.
    // Recibe los datos del usuario como atributos data-* del botón.
    // ═══════════════════════════════════════════════════════════════════════════

    document.querySelectorAll('.btn-abrir-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            // Leer datos del usuario desde los data-attributes del botón
            const userId = btn.dataset.userId;
            const nombre = btn.dataset.nombre;
            const email = btn.dataset.email;

            // Rellenar el modal con los datos del usuario seleccionado
            modalNombre.textContent = nombre;
            modalEmail.textContent = email;
            modalInputUsuarioId.value = userId;

            // Limpiar input previo
            modalInputTerminal.value = '';

            // Mostrar el modal
            modalOverlay.classList.add('visible');

            // Enfocar el primer input del modal para UX rápida
            setTimeout(() => modalInputTerminal.focus(), 100);
        });
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // MODAL: CERRAR
    // Se puede cerrar con: botón ✕, tecla Escape, o clic en el overlay.
    // ═══════════════════════════════════════════════════════════════════════════

    function cerrarModal() {
        modalOverlay.classList.remove('visible');
    }

    // Botón ✕ del modal
    if (btnCerrarModal) {
        btnCerrarModal.addEventListener('click', cerrarModal);
    }

    // Tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalOverlay.classList.contains('visible')) {
            cerrarModal();
        }
    });

    // Clic fuera del contenido del modal (en el overlay oscuro)
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                cerrarModal();
            }
        });
    }

});
