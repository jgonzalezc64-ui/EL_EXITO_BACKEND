# Modelos de tablas: Tienda, Mesa, EstadoOrden, TipoServicio, Orden, OrdenDetalle, OrdenDetalleModificador. TicketCocina no se mapea, se maneja en SQL con triggers
from django.db import models

class Tienda(models.Model):
    id_tienda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    codigo = models.CharField(max_length=50, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'pos.Tienda'

    def __str__(self): return f"{self.codigo} - {self.nombre}"


class Mesa(models.Model):
    id_mesa = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    activa = models.BooleanField(default=True)
    id_tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column='id_tienda', related_name='mesas')

    class Meta:
        managed = False
        db_table = 'pos.Mesa'
        unique_together = (('id_tienda', 'codigo'),)

    def __str__(self): return f"{self.id_tienda_id}:{self.codigo}"


class EstadoOrden(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        managed = False
        db_table = 'pos.EstadoOrden'

    def __str__(self): return self.nombre


class TipoServicio(models.Model):
    id_tipo_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        managed = False
        db_table = 'pos.TipoServicio'

    def __str__(self): return self.nombre


class Orden(models.Model):
    id_orden = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField()
    id_mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, db_column='id_mesa', null=True, blank=True)
    id_mesero = models.IntegerField(null=True, blank=True)  # si luego mapeas Usuario, cambias a FK
    id_estado = models.ForeignKey(EstadoOrden, on_delete=models.PROTECT, db_column='id_estado')
    id_tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.PROTECT, db_column='id_tipo_servicio')
    observaciones = models.CharField(max_length=250, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)  # columna calculada en SQL, la leemos

    class Meta:
        managed = False
        db_table = 'pos.Orden'


    def __str__(self): return f"Orden {self.id_orden}"


class OrdenDetalle(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_orden = models.ForeignKey(Orden, on_delete=models.CASCADE, db_column='id_orden', related_name='detalles')
    id_producto = models.IntegerField()  # podemos mapear FK a Producto si importamos el modelo
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    nota = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'pos.OrdenDetalle'



class OrdenDetalleModificador(models.Model):
    id_detalle = models.ForeignKey(OrdenDetalle, on_delete=models.CASCADE, db_column='id_detalle', related_name='mods')
    id_modificador = models.IntegerField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'pos.OrdenDetalleModificador'
        unique_together = (('id_detalle', 'id_modificador'),)
