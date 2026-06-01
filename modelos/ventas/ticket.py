import uuid
from django.db import models

class Ticket(models.Model):
    """
    Modelo Ticket: Representa el derecho de acceso individual a un asiento de una función.
    Está vinculado a una Venta maestra.
    
    ESTRATEGIA CONTRA CONDICIÓN DE CARRERA:
    El parámetro `unique_together` en la clase Meta garantiza a nivel motor de base de datos
    que no puedan existir jamás dos tickets para la misma función y el mismo asiento.
    """
    
    ESTADOS_USO = [
        ('pendiente', 'Pendiente de Validación'),
        ('validado', 'Ingreso Validado'),
    ]

    id_ticket = models.AutoField(primary_key=True)
    # Se genera un UUID por defecto para que el código del QR sea imposible de adivinar.
    codigo_qr = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    
    venta = models.ForeignKey(
        'sistema_cine.Venta', 
        on_delete=models.CASCADE, 
        related_name='tickets'
    )
    funcion = models.ForeignKey(
        'sistema_cine.Funcion', 
        on_delete=models.PROTECT, 
        related_name='tickets_vendidos'
    )
    asiento = models.ForeignKey(
        'sistema_cine.Asiento', 
        on_delete=models.PROTECT, 
        related_name='tickets_asociados'
    )
    
    estado_uso = models.CharField(max_length=20, choices=ESTADOS_USO, default='pendiente')
    fecha_validacion = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha y hora de validación'
    )
    imagen_qr = models.ImageField(upload_to='tickets_qr/', blank=True, null=True)

    class Meta:
        app_label = 'sistema_cine'
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        # ¡¡LA REGLA DE ORO DE LA CONCURRENCIA!!
        unique_together = ('funcion', 'asiento')

    def __str__(self):
        return f"Ticket {self.id_ticket} - F:{self.funcion.id_funcion} - A:{self.asiento.fila}{self.asiento.numero}"
