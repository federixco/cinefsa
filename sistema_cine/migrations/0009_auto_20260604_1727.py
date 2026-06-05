from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_cine', '0008_asiento_estado_asiento'),
    ]

    operations = [

        # ── TRIGGER 1A: Actualizar capacidad al insertar asiento ──────────
        migrations.RunSQL(
            sql="DROP TRIGGER IF EXISTS trg_asiento_after_insert;",
            reverse_sql=migrations.RunSQL.noop,
        ),
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
                        WHERE sala_id = NEW.sala_id AND estado_asiento = 'activo'
                    )
                    WHERE id = NEW.sala_id;
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_asiento_after_insert;",
        ),

        # ── TRIGGER 1B: Actualizar capacidad al eliminar asiento ──────────
        migrations.RunSQL(
            sql="DROP TRIGGER IF EXISTS trg_asiento_after_delete;",
            reverse_sql=migrations.RunSQL.noop,
        ),
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
                        WHERE sala_id = OLD.sala_id AND estado_asiento = 'activo'
                    )
                    WHERE id = OLD.sala_id;
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_asiento_after_delete;",
        ),

        # ── TRIGGER 1C: Actualizar capacidad al cambiar estado asiento ────
        migrations.RunSQL(
            sql="""
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
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_asiento_after_update;",
        ),

        # ── FUNCIÓN: Contar asientos disponibles (ACTIVOS) ────────────────
        migrations.RunSQL(
            sql="DROP FUNCTION IF EXISTS fn_asientos_disponibles;",
            reverse_sql=migrations.RunSQL.noop,
        ),
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
                    WHERE f.id = p_funcion_id AND a.estado_asiento = 'activo';

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
