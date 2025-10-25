from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.seguridad.permissions import IsAdmin, IsAdminOrReadOnly

from .models import Menu, MenuSeccion, MenuItem
from .serializers import MenuSerializer, MenuSeccionSerializer, MenuItemSerializer

class BaseCRUD(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []
    ordering = []

class MenuViewSet(BaseCRUD):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Menu.objects.all().order_by('-activo','nombre')
    serializer_class = MenuSerializer
    search_fields = ['nombre','canal']
    ordering = ['-activo','nombre']

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='publicar',permission_classes=[IsAdmin])
    def publicar(self, request, pk=None):
        m = self.get_object()
        m.activo = True
        m.save()
        return Response(MenuSerializer(m).data)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='despublicar',permission_classes=[IsAdmin])
    def despublicar(self, request, pk=None):
        m = self.get_object()
        m.activo = False
        m.save()
        return Response(MenuSerializer(m).data)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='agregar-items-por-categoria',permission_classes=[IsAdmin])
    def agregar_items_por_categoria(self, request, pk=None):
        """
        body: { id_categoria, id_seccion (opcional), visible=true/false }
        Inserta MenuItem para todos los productos de esa categoría que aún no estén en el menú.
        Requiere que existan productos con esa categoría.
        """
        from django.db import connection
        id_categoria = request.data.get('id_categoria')
        id_seccion = request.data.get('id_seccion')
        visible = request.data.get('visible', True)
        if not id_categoria:
            return Response({"detail":"id_categoria es requerido"}, status=400)

        # Inserción masiva via SQL minimiza roundtrips
        with connection.cursor() as cur:
            cur.execute("""
                INSERT INTO pos.MenuItem (id_menu, id_producto, id_seccion, visible, orden)
                SELECT %s, p.id_producto, %s, %s,
                       ROW_NUMBER() OVER (ORDER BY p.nombre)
                FROM pos.Producto p
                LEFT JOIN pos.MenuItem mi
                  ON mi.id_menu = %s AND mi.id_producto = p.id_producto
                WHERE p.id_categoria = %s
                  AND mi.id_menu_item IS NULL
            """, [pk, id_seccion, 1 if visible else 0, pk, id_categoria])

        return Response({"detail":"Items agregados si faltaban"}, status=201)


class MenuSeccionViewSet(BaseCRUD):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MenuSeccion.objects.all().order_by('id_menu','orden')
    serializer_class = MenuSeccionSerializer
    search_fields = ['nombre']
    ordering = ['id_menu','orden']

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='reordenar',permission_classes=[IsAdmin])
    def reordenar(self, request):
        """
        body: { id_menu, ordenes: [ {id_seccion, orden}, ... ] }
        """
        id_menu = request.data.get('id_menu')
        ordenes = request.data.get('ordenes', [])
        if not id_menu or not isinstance(ordenes, list):
            return Response({"detail":"id_menu y ordenes son requeridos"}, status=400)
        actualizados = 0
        for item in ordenes:
            sid, ordn = item.get('id_seccion'), item.get('orden')
            if sid is None or ordn is None: 
                continue
            actualizados += MenuSeccion.objects.filter(id_menu=id_menu, id_seccion=sid).update(orden=ordn)
        return Response({"actualizados": actualizados}, status=200)


class MenuItemViewSet(BaseCRUD):
    permission_classes = [IsAdmin]
    queryset = MenuItem.objects.all().order_by('id_menu','id_seccion','orden')
    serializer_class = MenuItemSerializer
    search_fields = []  # podríamos buscar por nombre de producto con join si quisieras
    ordering = ['id_menu','id_seccion','orden']

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='reordenar',permission_classes=[IsAdmin])
    def reordenar(self, request):
        """
        body: { id_menu, id_seccion (opcional), ordenes: [ {id_menu_item, orden}, ... ] }
        """
        id_menu = request.data.get('id_menu')
        id_seccion = request.data.get('id_seccion')
        ordenes = request.data.get('ordenes', [])
        if not id_menu or not isinstance(ordenes, list):
            return Response({"detail":"id_menu y ordenes son requeridos"}, status=400)
        qs = MenuItem.objects.filter(id_menu=id_menu)
        if id_seccion:
            qs = qs.filter(id_seccion=id_seccion)
        actualizados = 0
        for item in ordenes:
            iid, ordn = item.get('id_menu_item'), item.get('orden')
            if iid is None or ordn is None:
                continue
            actualizados += qs.filter(id_menu_item=iid).update(orden=ordn)
        return Response({"actualizados": actualizados}, status=200)
