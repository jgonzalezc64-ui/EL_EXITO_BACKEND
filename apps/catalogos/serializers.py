from rest_framework import serializers
from django.db import IntegrityError
from .models import (
    Categoria,
    Producto,
    ModificadorGrupo,
    Modificador,
    ProductoModificador,
)

# ---------- Categorías y Productos ----------

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            'id_producto', 'id_categoria', 'nombre', 'descripcion',
            'precio_base', 'activo', 'requiere_cocina'
        ]

    def validate_precio_base(self, v):
        if v is None or v < 0:
            raise serializers.ValidationError("precio_base debe ser >= 0")
        return v

    def validate(self, attrs):
        creating = self.instance is None

        if creating:
            if not attrs.get('id_categoria'):
                raise serializers.ValidationError({"id_categoria": "Requerido"})
            nombre = (attrs.get('nombre') or "").strip()
            if not nombre:
                raise serializers.ValidationError({"nombre": "Requerido"})
            if attrs.get('precio_base') is None:
                raise serializers.ValidationError({"precio_base": "Requerido"})
        else:
            # En PATCH, valida solo si el campo viene
            if 'nombre' in attrs and not (attrs['nombre'] or '').strip():
                raise serializers.ValidationError({"nombre": "No puede estar vacío"})
            if 'precio_base' in attrs and attrs['precio_base'] is None:
                raise serializers.ValidationError({"precio_base": "Requerido"})

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            # índice único (id_categoria, nombre) o similares
            raise serializers.ValidationError({
                "non_field_errors": ["Ya existe un producto con ese nombre en esta categoría."]
            })


# ---------- Modificadores ----------

class ModificadorSerializer(serializers.ModelSerializer):
    # Grupo anidado opcional (read-only)
    grupo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Modificador
        fields = [
            'id_modificador',
            'id_grupo',          # FK (id)
            'grupo',             # objeto anidado opcional
            'nombre',
            'precio_extra',
            'activo',
        ]

    def get_grupo(self, obj):
        g = obj.id_grupo
        if not g:
            return None
        return {
            'id_grupo': g.id_grupo,
            'nombre': g.nombre,
            'minimo': g.minimo,
            'maximo': g.maximo,
            'obligatorio': g.obligatorio,
        }


class ModificadorGrupoSerializer(serializers.ModelSerializer):
    modificadores = ModificadorSerializer(many=True, read_only=True)

    class Meta:
        model = ModificadorGrupo
        fields = [
            'id_grupo',
            'nombre',
            'descripcion',
            'minimo',
            'maximo',
            'obligatorio',
            'modificadores',
        ]


# ---------- Producto ↔ Modificador (tabla puente) ----------

class ProductoModificadorSerializer(serializers.ModelSerializer):
    # Representaciones anidadas (opcionales) para ver info de ambos lados
    producto = serializers.SerializerMethodField(read_only=True)
    modificador = ModificadorSerializer(source='id_modificador', read_only=True)

    class Meta:
        model = ProductoModificador
        fields = [
            'id_producto',      # FK (id)
            'id_modificador',   # FK (id)
            'producto',         # objeto anidado (compacto)
            'modificador',      # objeto anidado (detallado)
        ]

    def get_producto(self, obj):
        p = obj.id_producto
        if not p:
            return None
        return {
            'id_producto': p.id_producto,
            'id_categoria': p.id_categoria_id,
            'nombre': p.nombre,
            'precio_base': str(p.precio_base),
            'requiere_cocina': p.requiere_cocina,
            'activo': p.activo,
        }
