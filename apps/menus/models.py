#Modelo para tablas Menu, MenuSeccion, MenuItem
from django.db import models

class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    id_tienda = models.IntegerField()  # FK soft a pos.Tienda
    nombre = models.CharField(max_length=120)
    canal = models.CharField(max_length=40, null=True, blank=True)
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'pos.Menu'
        unique_together = (('id_tienda','nombre'),)

    def __str__(self): return f"{self.nombre} (tienda {self.id_tienda})"


class MenuSeccion(models.Model):
    id_seccion = models.AutoField(primary_key=True)
    id_menu = models.IntegerField()
    id_categoria = models.IntegerField(null=True, blank=True)  # FK soft a pos.Categoria
    nombre = models.CharField(max_length=120)
    visible = models.BooleanField(default=True)
    orden = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'pos.MenuSeccion'

    def __str__(self): return f"{self.nombre} (menu {self.id_menu})"


class MenuItem(models.Model):
    id_menu_item = models.AutoField(primary_key=True)
    id_menu = models.IntegerField()
    id_producto = models.IntegerField()
    id_seccion = models.IntegerField(null=True, blank=True)
    precio_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    visible = models.BooleanField(default=True)
    orden = models.IntegerField(default=1)
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'pos.MenuItem'
        unique_together = (('id_menu','id_producto'),)

    def __str__(self): return f"Item {self.id_menu_item} ({self.id_menu} -> {self.id_producto})"
