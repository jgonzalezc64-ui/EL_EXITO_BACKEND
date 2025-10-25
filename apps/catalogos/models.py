# Modelos de tablas: Categoria, Producto, ModificadorGrupo, Modificador, ProductoModificador.

from django.db import models


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'pos.Categoria'


    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.PROTECT,           # coincide con tu FK (sin ON DELETE CASCADE)
        db_column='id_categoria',
        related_name='productos'
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=250, null=True, blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    requiere_cocina = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'pos.Producto'


    def __str__(self):
        return self.nombre


class ModificadorGrupo(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    minimo = models.IntegerField(default=0)
    maximo = models.IntegerField(default=5)
    obligatorio = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'pos.ModificadorGrupo'


    def __str__(self):
        return self.nombre


class Modificador(models.Model):
    id_modificador = models.AutoField(primary_key=True)
    id_grupo = models.ForeignKey(
        'ModificadorGrupo',
        on_delete=models.PROTECT,
        db_column='id_grupo',
        related_name='modificadores'
    )
    nombre = models.CharField(max_length=80)
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'pos.Modificador'

    def __str__(self):
        return self.nombre


class ProductoModificador(models.Model):
    # En SQL Server: PK compuesta (id_producto, id_modificador)
    # En Django: marcamos id_producto como PK para cumplir ORM; preservamos unicidad compuesta.
    id_producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='producto_modificadores',
        primary_key=True
    )
    id_modificador = models.ForeignKey(
        'Modificador',
        on_delete=models.CASCADE,
        db_column='id_modificador',
        related_name='modificador_productos'
    )

    class Meta:
        managed = False
        db_table = 'pos.ProductoModificador'


    def __str__(self):
        return f'{self.id_producto_id} ↔ {self.id_modificador_id}'

