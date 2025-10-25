#Tablas Rol y Usuario (pos.Rol, pos.Usuario)
from django.db import models

class RolPOS(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)
    class Meta:
        managed = False
        db_table = 'pos.Rol'
    def __str__(self): return self.nombre

class UsuarioPOS(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    correo = models.CharField(max_length=150, unique=True, null=True, blank=True)
    id_rol = models.ForeignKey(RolPOS, on_delete=models.PROTECT, db_column='id_rol')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'pos.Usuario'
