from django.db import models

class MetodoPago(models.Model):
    id_metodo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40, unique=True)
    class Meta:
        managed = False
        db_table = 'pos.MetodoPago'
    def __str__(self): return self.nombre

class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_orden = models.IntegerField()  # FK soft a pos.Orden
    id_metodo = models.IntegerField() # FK soft a MetodoPago
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField()
    referencia = models.CharField(max_length=80, null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'pos.Pago'
