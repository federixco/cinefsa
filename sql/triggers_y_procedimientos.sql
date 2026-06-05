-- =============================================================================
-- triggers_y_procedimientos.sql
-- Sistema CineFSA — Objetos programados de base de datos (MySQL)
--
-- Contiene:
--   TRIGGER 1: trg_asiento_after_insert / trg_asiento_after_delete
--              Actualizar capacidad_maxima de sala al agregar/eliminar asientos.
--
--   TRIGGER 2: trg_ticket_check_mantenimiento
--              Impedir venta de ticket si la sala está en mantenimiento.
--
--   PROCEDIMIENTO: sp_generar_id_validador
--                  Genera el siguiente id_validador con prefijo 'emp-'.
--
--   FUNCIÓN: fn_asientos_disponibles
--            Devuelve la cantidad de asientos libres para una función.
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER 1A: Actualizar capacidad al INSERTAR un asiento
-- ─────────────────────────────────────────────────────────────────────────────
-- Después de insertar un nuevo asiento en una sala, recalcula la capacidad
-- máxima contando todos los asientos asociados a esa sala.
-- Esto mantiene la columna capacidad_maxima siempre sincronizada con la
-- cantidad real de butacas, sin intervención manual.
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_asiento_after_insert;

DELIMITER //

CREATE TRIGGER trg_asiento_after_insert
AFTER INSERT ON asiento
FOR EACH ROW
BEGIN
    UPDATE sala
    SET capacidad_maxima = (
        SELECT COUNT(*)
        FROM asiento
        WHERE sala_id = NEW.sala_id AND estado_asiento = 'activo'
    )
    WHERE id = NEW.sala_id;
END //

DELIMITER ;


-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER 1B: Actualizar capacidad al ELIMINAR un asiento
-- ─────────────────────────────────────────────────────────────────────────────
-- Complemento del trigger anterior. Al eliminar un asiento, recalcula la
-- capacidad para que refleje la nueva cantidad real de butacas.
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_asiento_after_delete;

DELIMITER //

CREATE TRIGGER trg_asiento_after_delete
AFTER DELETE ON asiento
FOR EACH ROW
BEGIN
    UPDATE sala
    SET capacidad_maxima = (
        SELECT COUNT(*)
        FROM asiento
        WHERE sala_id = OLD.sala_id AND estado_asiento = 'activo'
    )
    WHERE id = OLD.sala_id;
END //

DELIMITER ;


-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER 1C: Actualizar capacidad al ACTUALIZAR un asiento (Baja Lógica)
-- ─────────────────────────────────────────────────────────────────────────────
-- Si un asiento cambia de estado (ej: activo a inactivo), se recalcula.
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_asiento_after_update;

DELIMITER //

CREATE TRIGGER trg_asiento_after_update
AFTER UPDATE ON asiento
FOR EACH ROW
BEGIN
    IF NEW.estado_asiento != OLD.estado_asiento THEN
        UPDATE sala
        SET capacidad_maxima = (
            SELECT COUNT(*)
            FROM asiento
            WHERE sala_id = NEW.sala_id AND estado_asiento = 'activo'
        )
        WHERE id = NEW.sala_id;
    END IF;
END //

DELIMITER ;


-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER 2: Impedir venta de ticket si la sala está en mantenimiento
-- ─────────────────────────────────────────────────────────────────────────────
-- Antes de insertar un ticket, verifica el estado de la sala asociada a la
-- función. Si la sala está en mantenimiento, lanza un error SQL con
-- SIGNAL SQLSTATE '45000' que aborta la inserción.
--
-- Esto actúa como una barrera de seguridad a nivel de base de datos:
-- incluso si la aplicación tiene un bug y no valida el estado de la sala,
-- el trigger impide la inserción corrupta.
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_ticket_check_mantenimiento;

DELIMITER //

CREATE TRIGGER trg_ticket_check_mantenimiento
BEFORE INSERT ON ticket
FOR EACH ROW
BEGIN
    DECLARE v_estado_sala VARCHAR(15);

    -- Obtener el estado de la sala a través de la función asociada al ticket
    SELECT s.estado
    INTO v_estado_sala
    FROM funcion f
    INNER JOIN sala s ON f.sala_id = s.id
    WHERE f.id = NEW.funcion_id;

    -- Si la sala está en mantenimiento, rechazar la operación
    IF v_estado_sala = 'mantenimiento' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERROR: No se puede emitir ticket. La sala se encuentra en mantenimiento.';
    END IF;
END //

DELIMITER ;


-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDIMIENTO: Generar siguiente id_validador para empleados
-- ─────────────────────────────────────────────────────────────────────────────
-- Busca el último id_validador con prefijo 'emp-' en la tabla empleado,
-- extrae la parte numérica, le suma 1 y devuelve el nuevo ID formateado.
--
-- Uso:
--   CALL sp_generar_id_validador(@nuevo_id);
--   SELECT @nuevo_id;  -- Resultado: 'emp-001', 'emp-002', etc.
--
-- Si no existen empleados, devuelve 'emp-001'.
-- ─────────────────────────────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS sp_generar_id_validador;

DELIMITER //

CREATE PROCEDURE sp_generar_id_validador(OUT p_nuevo_id VARCHAR(50))
BEGIN
    DECLARE v_ultimo_numero INT DEFAULT 0;

    -- Extraer la parte numérica del último id_validador con prefijo 'emp-'
    -- SUBSTRING(id_validador, 5) toma desde el 5to carácter en adelante: 'emp-007' → '007'
    -- CAST(... AS UNSIGNED) convierte '007' a 7
    -- MAX() obtiene el número más alto
    -- COALESCE(..., 0) devuelve 0 si no hay registros
    SELECT COALESCE(
        MAX(CAST(SUBSTRING(id_validador, 5) AS UNSIGNED)), 0
    )
    INTO v_ultimo_numero
    FROM empleado
    WHERE id_validador LIKE 'emp-%';

    -- Formatear: sumar 1 y rellenar con ceros hasta 3 dígitos
    -- LPAD(8, 3, '0') → '008'
    SET p_nuevo_id = CONCAT('emp-', LPAD(v_ultimo_numero + 1, 3, '0'));
END //

DELIMITER ;


-- ─────────────────────────────────────────────────────────────────────────────
-- FUNCIÓN: Contar asientos disponibles para una función
-- ─────────────────────────────────────────────────────────────────────────────
-- Recibe el ID de una función y devuelve un entero con la cantidad de
-- asientos que aún no fueron vendidos (no tienen ticket asociado).
--
-- Uso:
--   SELECT fn_asientos_disponibles(15);  -- Resultado: 42
--
-- Cálculo: (total asientos de la sala) - (tickets emitidos para esa función)
-- Se puede usar en la cartelera para mostrar "X lugares disponibles".
-- ─────────────────────────────────────────────────────────────────────────────

DROP FUNCTION IF EXISTS fn_asientos_disponibles;

DELIMITER //

CREATE FUNCTION fn_asientos_disponibles(p_funcion_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total_asientos INT DEFAULT 0;
    DECLARE v_tickets_vendidos INT DEFAULT 0;

    -- Contar el total de asientos ACTIVOS de la sala asignada a esta función
    SELECT COUNT(*)
    INTO v_total_asientos
    FROM asiento a
    INNER JOIN funcion f ON a.sala_id = f.sala_id
    WHERE f.id = p_funcion_id AND a.estado_asiento = 'activo';

    -- Contar los tickets ya emitidos para esta función
    SELECT COUNT(*)
    INTO v_tickets_vendidos
    FROM ticket
    WHERE funcion_id = p_funcion_id;

    -- Devolver la diferencia: asientos libres
    RETURN v_total_asientos - v_tickets_vendidos;
END //

DELIMITER ;
