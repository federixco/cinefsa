"""
Migración: Crear triggers, procedimiento y función SQL en MySQL.

Objetos creados:
  - TRIGGER trg_asiento_after_insert: Actualiza capacidad_maxima al insertar asiento.
  - TRIGGER trg_asiento_after_delete: Actualiza capacidad_maxima al eliminar asiento.
  - TRIGGER trg_ticket_check_mantenimiento: Impide ticket si sala en mantenimiento.
  - PROCEDURE sp_generar_id_validador: Genera siguiente emp-XXX.
  - FUNCTION fn_asientos_disponibles: Cuenta asientos libres por función.

Nota: Se usa migrations.RunSQL con sql (forward) y reverse_sql (rollback).
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_cine', '0005_merge_20260531_0200'),
    ]

    operations = [

        # ── TRIGGER 1A: Actualizar capacidad al insertar asiento ──────────
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER trg_asiento_after_insert
                AFTER INSERT ON asiento
                FOR EACH ROW
                BEGIN
                    UPDATE sala
                    SET capacidad_maxima = (
                        SELECT COUNT(*)
                        FROM asiento
                        WHERE sala_id = NEW.sala_id
                    )
                    WHERE id = NEW.sala_id;
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_asiento_after_insert;",
        ),

        # ── TRIGGER 1B: Actualizar capacidad al eliminar asiento ──────────
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER trg_asiento_after_delete
                AFTER DELETE ON asiento
                FOR EACH ROW
                BEGIN
                    UPDATE sala
                    SET capacidad_maxima = (
                        SELECT COUNT(*)
                        FROM asiento
                        WHERE sala_id = OLD.sala_id
                    )
                    WHERE id = OLD.sala_id;
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_asiento_after_delete;",
        ),

        # ── TRIGGER 2: Impedir ticket si sala en mantenimiento ────────────
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER trg_ticket_check_mantenimiento
                BEFORE INSERT ON ticket
                FOR EACH ROW
                BEGIN
                    DECLARE v_estado_sala VARCHAR(15);

                    SELECT s.estado
                    INTO v_estado_sala
                    FROM funcion f
                    INNER JOIN sala s ON f.sala_id = s.id
                    WHERE f.id = NEW.funcion_id;

                    IF v_estado_sala = 'mantenimiento' THEN
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = 'ERROR: No se puede emitir ticket. La sala se encuentra en mantenimiento.';
                    END IF;
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_ticket_check_mantenimiento;",
        ),

        # ── PROCEDIMIENTO: Generar siguiente id_validador ─────────────────
        migrations.RunSQL(
            sql="""
                CREATE PROCEDURE sp_generar_id_validador(OUT p_nuevo_id VARCHAR(50))
                BEGIN
                    DECLARE v_ultimo_numero INT DEFAULT 0;

                    SELECT COALESCE(
                        MAX(CAST(SUBSTRING(id_validador, 5) AS UNSIGNED)), 0
                    )
                    INTO v_ultimo_numero
                    FROM empleado
                    WHERE id_validador LIKE 'emp-%%';

                    SET p_nuevo_id = CONCAT('emp-', LPAD(v_ultimo_numero + 1, 3, '0'));
                END;
            """,
            reverse_sql="DROP PROCEDURE IF EXISTS sp_generar_id_validador;",
        ),

        # ── FUNCIÓN: Contar asientos disponibles ──────────────────────────
        migrations.RunSQL(
            sql="""
                CREATE FUNCTION fn_asientos_disponibles(p_funcion_id INT)
                RETURNS INT
                DETERMINISTIC
                READS SQL DATA
                BEGIN
                    DECLARE v_total_asientos INT DEFAULT 0;
                    DECLARE v_tickets_vendidos INT DEFAULT 0;

                    SELECT COUNT(*)
                    INTO v_total_asientos
                    FROM asiento a
                    INNER JOIN funcion f ON a.sala_id = f.sala_id
                    WHERE f.id = p_funcion_id;

                    SELECT COUNT(*)
                    INTO v_tickets_vendidos
                    FROM ticket
                    WHERE funcion_id = p_funcion_id;

                    RETURN v_total_asientos - v_tickets_vendidos;
                END;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS fn_asientos_disponibles;",
        ),
    ]
