#Modelo para tabla TicketCocina, SE LLENA CON TRIGGER 
from django.db import models

class TicketCocina(models.Model):
    id_ticket = models.AutoField(primary_key=True)
    id_orden = models.IntegerField(unique=True)
    fecha_generado = models.DateTimeField()
    estado = models.CharField(max_length=20)  # 'PENDIENTE','EN_PREPARACION','LISTO','ENTREGADO'

    class Meta:
        managed = False
        db_table = 'pos.TicketCocina'

    def __str__(self):
        return f"Ticket {self.id_ticket} (Orden {self.id_orden})"
