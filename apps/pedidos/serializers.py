from decimal import Decimal
from rest_framework import serializers
from .models import (
    Tienda, Mesa, EstadoOrden, TipoServicio,
    Orden, OrdenDetalle, OrdenDetalleModificador
)

# -----------------------------------------------------------------------------
# jose: Campos numéricos/monetarios que el frontend necesita como *number*
# (no string) para poder usar .toFixed(2) sin errores.
# DRF por defecto serializa Decimal como string. Creamos campos que devuelven
# float en la representación.
# -----------------------------------------------------------------------------
class _BaseNumberField(serializers.DecimalField):  # jose
    def to_representation(self, value):            # jose
        # value puede venir como Decimal, str o None
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            # Si algo raro llega, regresa lo que DRF haría
            return super().to_representation(value)

class MoneyField(_BaseNumberField):                # jose
    """
    Para dinero: 2 decimales por convención.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 12)
        kwargs.setdefault("decimal_places", 2)
        super().__init__(*args, **kwargs)

class QtyField(_BaseNumberField):                  # jose
    """
    Para cantidades; si usas enteros, puedes cambiar decimal_places=0.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 10)
        kwargs.setdefault("decimal_places", 2)
        super().__init__(*args, **kwargs)


class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['id_tienda', 'nombre', 'codigo', 'activa']


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id_mesa', 'codigo', 'ubicacion', 'activa', 'id_tienda']


class EstadoOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoOrden
        fields = ['id_estado', 'nombre']


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ['id_tipo_servicio', 'nombre']


class OrdenDetalleModSerializer(serializers.ModelSerializer):
    # jose: exponemos FKs y valores; normalizamos numéricos a number
    cantidad = QtyField()         # jose
    precio_extra = MoneyField()   # jose

    class Meta:
        model = OrdenDetalleModificador
        fields = ['id_detalle', 'id_modificador', 'cantidad', 'precio_extra']


class OrdenDetalleSerializer(serializers.ModelSerializer):
    # jose: relación inversa por defecto si el modelo NO tiene related_name
    # Si tienes related_name distinto, ajústalo aquí.
    mods = OrdenDetalleModSerializer(
        source='ordendetallemodificador_set', many=True, read_only=True
    )  # jose

    # jose: numéricos como number
    cantidad = QtyField()          # jose
    precio_unitario = MoneyField() # jose

    class Meta:
        model = OrdenDetalle
        fields = [
            'id_detalle', 'id_orden', 'id_producto',
            'cantidad', 'precio_unitario', 'nota', 'mods'
        ]


class OrdenSerializer(serializers.ModelSerializer):
    # jose: relaciones legibles
    estado = EstadoOrdenSerializer(source='id_estado', read_only=True)                 # jose
    tipo_servicio = TipoServicioSerializer(source='id_tipo_servicio', read_only=True)  # jose

    # jose: detalles por relación inversa por defecto (ajusta si tienes related_name)
    detalles = OrdenDetalleSerializer(
        source='ordendetalle_set', many=True, read_only=True
    )  # jose

    # jose: monetarios como number (no string)
    subtotal = MoneyField(read_only=True)   # jose
    descuento = MoneyField(read_only=True)  # jose
    total = MoneyField(read_only=True)      # jose

    class Meta:
        model = Orden
        fields = [
            'id_orden', 'fecha_hora', 'id_mesa', 'id_mesero',
            'id_estado', 'estado', 'id_tipo_servicio', 'tipo_servicio',
            'observaciones', 'subtotal', 'descuento', 'total',
            'detalles'
        ]


# --- Serializer para la vista pos.vw_OrdenDetalleProducto ---
class OrdenDetalleVWSerializer(serializers.Serializer):
    id_detalle = serializers.IntegerField()
    id_orden = serializers.IntegerField()
    id_producto = serializers.IntegerField()
    nombre_producto = serializers.CharField()
    cantidad = QtyField(read_only=True)           # <-- CAMBIO: antes NumberField
    precio_unitario = MoneyField(read_only=True)
    nota = serializers.CharField(allow_null=True, required=False)
