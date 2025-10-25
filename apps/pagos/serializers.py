from rest_framework import serializers
from .models import MetodoPago, Pago

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id_metodo','nombre']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id_pago','id_orden','id_metodo','monto','fecha_hora','referencia']
