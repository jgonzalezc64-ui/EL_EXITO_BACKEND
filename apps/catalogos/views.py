from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.seguridad.permissions import IsAdmin, IsAdminOrReadOnly

from .models import (
    Categoria, Producto, ModificadorGrupo, Modificador, ProductoModificador
)
from .serializers import (
    CategoriaSerializer, ProductoSerializer,
    ModificadorGrupoSerializer, ModificadorSerializer,
    ProductoModificadorSerializer
)


class BaseCRUDViewSet(viewsets.ModelViewSet):
    """Base con CRUD + filtros comunes."""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []
    ordering = []


class CategoriaViewSet(BaseCRUDViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


class ProductoViewSet(BaseCRUDViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    queryset = (
        Producto.objects.select_related('id_categoria')
        .all().order_by('nombre')
    )
    serializer_class = ProductoSerializer
    search_fields = ['nombre', 'descripcion', 'id_categoria__nombre']
    ordering = ['nombre']


class ModificadorGrupoViewSet(BaseCRUDViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    queryset = ModificadorGrupo.objects.all().order_by('nombre')
    serializer_class = ModificadorGrupoSerializer
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


class ModificadorViewSet(BaseCRUDViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    queryset = (
        Modificador.objects.select_related('id_grupo')
        .all().order_by('nombre')
    )
    serializer_class = ModificadorSerializer
    search_fields = ['nombre', 'id_grupo__nombre']
    ordering = ['nombre']


class ProductoModificadorViewSet(viewsets.GenericViewSet):
    """
    Lista y manejo de relaciones Producto<->Modificador.
    - GET /producto-modificadores/                      -> lista (read)
    - POST /producto-modificadores/ {id_producto,id_modificador}     -> crear vínculo
    - POST /producto-modificadores/remove {id_producto,id_modificador} -> eliminar vínculo
      (Usamos POST para remove por comodidad del front; DELETE no admite body)
    """
    permission_classes = [IsAdmin]
    serializer_class = ProductoModificadorSerializer

    def get_queryset(self):
        qs = (ProductoModificador.objects
              .select_related('id_producto', 'id_modificador', 'id_modificador__id_grupo')
              .all()
              .order_by('id_producto__nombre', 'id_modificador__nombre'))
        # filtros opcionales por querystring: ?id_producto=1, ?id_modificador=2
        idp = self.request.query_params.get('id_producto')
        idm = self.request.query_params.get('id_modificador')
        if idp:
            qs = qs.filter(id_producto_id=idp)
        if idm:
            qs = qs.filter(id_modificador_id=idm)
        return qs

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        id_producto = request.data.get('id_producto')
        id_modificador = request.data.get('id_modificador')
        if not id_producto or not id_modificador:
            return Response(
                {"detail": "id_producto e id_modificador son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # evitar duplicados (PK compuesta en SQL)
        exists = ProductoModificador.objects.filter(
            id_producto_id=id_producto, id_modificador_id=id_modificador
        ).exists()
        if exists:
            return Response({"detail": "La relación ya existe."}, status=status.HTTP_200_OK)

        obj = ProductoModificador.objects.create(
            id_producto_id=id_producto,
            id_modificador_id=id_modificador
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='remove')
    def remove_relation(self, request):
        id_producto = request.data.get('id_producto')
        id_modificador = request.data.get('id_modificador')
        if not id_producto or not id_modificador:
            return Response(
                {"detail": "id_producto e id_modificador son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        deleted, _ = (ProductoModificador.objects
                      .filter(id_producto_id=id_producto, id_modificador_id=id_modificador)
                      .delete())
        if deleted == 0:
            return Response({"detail": "No se encontró la relación."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
