from rest_framework import serializers
from .models import TicketCocina

class TicketCocinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCocina
        fields = ['id_ticket', 'id_orden', 'fecha_generado', 'estado']
