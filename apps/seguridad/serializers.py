from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import RolPOS, UsuarioPOS

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','is_active','is_staff']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','password','first_name','last_name','email','is_active','is_staff']
    def create(self, validated_data):
        pwd = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']

# Solo si exponemos lectura de tus tablas POS:
class RolPOSSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPOS
        fields = ['id_rol','nombre']

class UsuarioPOSSerializer(serializers.ModelSerializer):
    rol = RolPOSSerializer(source='id_rol', read_only=True)
    class Meta:
        model = UsuarioPOS
        fields = ['id_usuario','nombre','correo','id_rol','rol','activo','fecha_creacion']
