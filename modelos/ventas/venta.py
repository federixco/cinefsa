from django.db import models
from django.utils.timezone import now

class Venta(models.Model):
    """
    Modelo Venta: Representa la transacción económica.
    Puede ser generada por un Cliente (compra web) o por un Empleado (boletería física).
    Por eso la relación apunta directamente a la tabla base de Usuario.
    """
    
    METODOS_PAGO = [
        ('mercado_pago', 'Mercado Pago'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('efectivo', 'Efectivo en Boletería'),
    ]

    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    id_venta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        'sistema_cine.Usuario', 
        on_delete=models.PROTECT, 
        related_name='ventas'
    )
    fecha_hora_transaccion = models.DateTimeField(default=now)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_hora_transaccion']

    def __str__(self):
        return f"Venta #{self.id_venta} - {self.usuario.nombre_completo} - ${self.monto_total}"
