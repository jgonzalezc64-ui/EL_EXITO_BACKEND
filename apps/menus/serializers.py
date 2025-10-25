from rest_framework import serializers
from .models import Menu, MenuSeccion, MenuItem

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = [
            'id_menu','id_tienda','nombre','canal',
            'vigente_desde','vigente_hasta','activo'
        ]

class MenuSeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuSeccion
        fields = [
            'id_seccion','id_menu','id_categoria','nombre',
            'visible','orden'
        ]

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            'id_menu_item','id_menu','id_producto','id_seccion',
            'precio_override','visible','orden','vigente_desde','vigente_hasta'
        ]
