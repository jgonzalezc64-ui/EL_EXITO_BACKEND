# apps/pedidos/admin_views.py
from rest_framework import viewsets, filters, permissions
from apps.seguridad.permissions import IsAdmin  # asegúrate que existe
from .models import Tienda, Mesa, EstadoOrden, TipoServicio
from .serializers import (
    TiendaSerializer, MesaSerializer, EstadoOrdenSerializer, TipoServicioSerializer
)

# jose: Base CRUD para admin (usa filtros comunes)
class AdminBaseCRUD(viewsets.ModelViewSet):  # jose
    permission_classes = [IsAdmin]  # jose: sólo ADMIN
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # jose
    search_fields = []  # jose
    ordering = []  # jose


class AdminTiendaViewSet(AdminBaseCRUD):  # jose
    queryset = Tienda.objects.all().order_by('nombre')
    serializer_class = TiendaSerializer
    search_fields = ['nombre', 'codigo']  # jose
    ordering = ['nombre']  # jose


class AdminMesaViewSet(AdminBaseCRUD):  # jose
    queryset = Mesa.objects.select_related('id_tienda').all().order_by('id_tienda__nombre', 'codigo')
    serializer_class = MesaSerializer
    search_fields = ['codigo', 'ubicacion', 'id_tienda__nombre']  # jose
    ordering = ['id_tienda__nombre', 'codigo']  # jose


class AdminEstadoOrdenViewSet(AdminBaseCRUD):  # jose
    queryset = EstadoOrden.objects.all().order_by('nombre')
    serializer_class = EstadoOrdenSerializer
    search_fields = ['nombre']  # jose
    ordering = ['nombre']  # jose


class AdminTipoServicioViewSet(AdminBaseCRUD):  # jose
    queryset = TipoServicio.objects.all().order_by('nombre')
    serializer_class = TipoServicioSerializer
    search_fields = ['nombre']  # jose
    ordering = ['nombre']  # jose
