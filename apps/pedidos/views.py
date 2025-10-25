from django.db import transaction, connection  # jose
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from apps.seguridad.permissions import IsAdmin

from .models import (
    Tienda, Mesa, EstadoOrden, TipoServicio,
    Orden, OrdenDetalle, OrdenDetalleModificador
)
from .serializers import (
    TiendaSerializer, MesaSerializer, EstadoOrdenSerializer, TipoServicioSerializer,
    OrdenSerializer, OrdenDetalleSerializer, OrdenDetalleModSerializer,
    OrdenDetalleVWSerializer,   # ⟵ AÑADIDO
)

# ---- Reglas de roles ---------------------------------------------------------

# jose: roles que PUEDEN operar pedidos (abrir/editar/cerrar/listar)
ORDER_ROLES = ['ADMIN', 'MESERO', 'CAJA']  # jose
# jose: cocina NO tiene permisos para pedidos

def _require_role(request, allowed_groups: list[str]):
    """Pequeño helper para validar grupo/rol."""
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    # --- jose: permitir superusuario sin exigir pertenencia a grupos ---
    if getattr(request.user, "is_superuser", False):  # jose
        return  # jose
    # -------------------------------------------------------------------
    if not request.user.groups.filter(name__in=allowed_groups).exists():
        raise PermissionDenied("No tiene permisos para esta acción")


# ==============================================================================
#  CATÁLOGOS PUBLICOS (solo lectura para cualquier autenticado)
# ==============================================================================

class TiendaViewSet(viewsets.ReadOnlyModelViewSet):  # jose
    permission_classes = [IsAuthenticated]           # jose (antes IsAdmin)
    queryset = Tienda.objects.all().order_by('nombre')
    serializer_class = TiendaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # jose
    search_fields = ['nombre', 'codigo']                               # jose
    ordering = ['nombre']                                              # jose


class MesaViewSet(viewsets.ReadOnlyModelViewSet):  # jose
    permission_classes = [IsAuthenticated]         # jose (antes IsAdmin)
    queryset = Mesa.objects.select_related('id_tienda').all().order_by('id_tienda__nombre', 'codigo')
    serializer_class = MesaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]   # jose
    search_fields = ['codigo', 'ubicacion', 'id_tienda__nombre']       # jose
    ordering = ['id_tienda__nombre', 'codigo']                         # jose


class EstadoOrdenViewSet(viewsets.ReadOnlyModelViewSet):  # jose
    permission_classes = [IsAuthenticated]                          # jose (antes IsAdmin)
    queryset = EstadoOrden.objects.all().order_by('nombre')
    serializer_class = EstadoOrdenSerializer


class TipoServicioViewSet(viewsets.ReadOnlyModelViewSet):  # jose
    permission_classes = [IsAuthenticated]
    queryset = TipoServicio.objects.all().order_by('nombre')
    serializer_class = TipoServicioSerializer


# ==============================================================================
#  CATÁLOGOS ADMIN (CRUD completo, SOLO ADMIN)
# ==============================================================================

class BaseCRUD(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]  # NO usar directo; cada AdminViewSet redefine permiso  # jose
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []
    ordering = []


class TiendaAdminViewSet(BaseCRUD):  # jose NUEVO
    permission_classes = [IsAdmin]    # jose
    queryset = Tienda.objects.all().order_by('nombre')
    serializer_class = TiendaSerializer
    search_fields = ['nombre', 'codigo']
    ordering = ['nombre']


class MesaAdminViewSet(BaseCRUD):  # jose NUEVO
    permission_classes = [IsAdmin]   # jose
    queryset = Mesa.objects.select_related('id_tienda').all().order_by('id_tienda__nombre', 'codigo')
    serializer_class = MesaSerializer
    search_fields = ['codigo', 'ubicacion', 'id_tienda__nombre']
    ordering = ['id_tienda__nombre', 'codigo']


class EstadoOrdenAdminViewSet(BaseCRUD):  # jose NUEVO
    permission_classes = [IsAdmin]         # jose
    queryset = EstadoOrden.objects.all().order_by('nombre')
    serializer_class = EstadoOrdenSerializer
    search_fields = ['nombre']
    ordering = ['nombre']


class TipoServicioAdminViewSet(BaseCRUD):  # jose NUEVO
    permission_classes = [IsAdmin]          # jose
    queryset = TipoServicio.objects.all().order_by('nombre')
    serializer_class = TipoServicioSerializer
    search_fields = ['nombre']
    ordering = ['nombre']


# ==============================================================================
#  ORDENES (negocio)
# ==============================================================================

class OrdenViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrdenSerializer

    def get_queryset(self):
        return (
            Orden.objects
            .select_related('id_estado', 'id_tipo_servicio', 'id_mesa')
            .all()
            .order_by('-fecha_hora', '-id_orden')
        )

    # Listar
    def list(self, request, *args, **kwargs):
        _require_role(request, ORDER_ROLES)  # jose

        user = request.user  # jose
        qs = self.get_queryset()  # jose

        # jose: detecta rol ya sea por Django Group o por tu tabla pos.Usuario.id_rol
        is_super = getattr(user, 'is_superuser', False)  # jose
        user_groups = set(user.groups.values_list('name', flat=True)) if user.is_authenticated else set()  # jose
        # --- map por BD (si tienes el modelo Usuario mapeado o property en request.user) ---
        user_id_rol = getattr(user, 'id_rol', None)  # jose (si tu User extiende y guarda id_rol)
        # Equivalencias:
        is_cocina = ('COCINA' in user_groups) or (user_id_rol == 3)  # jose

        if is_cocina and not is_super:
            # KDS ve sólo lo que está EN_COCINA
            qs = qs.filter(id_estado__nombre='EN_COCINA')  # jose
        else:
            # Resto NO ve lo que está en cocina
            qs = qs.exclude(id_estado__nombre='EN_COCINA')  # jose

        ser = self.get_serializer(qs, many=True)  # jose
        return Response(ser.data)  # jose


    # Detalle
    def retrieve(self, request, pk=None, *args, **kwargs):
        _require_role(request, ORDER_ROLES)  # jose
        o = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(o).data)

    # --- listar detalles de una orden (modelo) ---
    @action(detail=True, methods=['get'], url_path='detalles')  # jose
    def detalles(self, request, pk=None):  # jose
        _require_role(request, ORDER_ROLES)  # jose
        qs = (
            OrdenDetalle.objects
            .filter(id_orden_id=pk)
            .order_by('id_detalle')
        )
        ser = OrdenDetalleSerializer(qs, many=True)
        return Response(ser.data)

    # --- NUEVO: listar detalles desde la VISTA con nombre_producto ---
    @action(detail=True, methods=['get'], url_path='detalles-vw')  # jose
    def detalles_vw(self, request, pk=None):  # jose
        """
        Devuelve los detalles de la orden leyendo la vista pos.vw_OrdenDetalleProducto,
        que ya incluye 'nombre_producto'.
        GET /api/v1/pedidos/ordenes/<id>/detalles-vw/
        """
        _require_role(request, ORDER_ROLES)  # jose

        with connection.cursor() as cur:  # jose
            cur.execute("""
                SELECT  id_detalle,
                        id_orden,
                        id_producto,
                        nombre_producto,
                        cantidad,
                        precio_unitario,
                        nota
                  FROM pos.vw_OrdenDetalleProducto
                 WHERE id_orden = %s
                 ORDER BY id_detalle ASC
            """, [pk])
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        ser = OrdenDetalleVWSerializer(rows, many=True)  # jose
        return Response(ser.data, status=200)  # jose

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='abrir')
    def abrir(self, request):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: {
          id_tipo_servicio:int (requerido),
          id_mesa:int (opcional, sólo si servicio = MESA),
          id_mesero:int (opcional; si no viene se toma del usuario),
          observaciones?: str
        }
        """
        # ----------------------- ENTRADA --------------------------------------
        id_tipo_servicio = request.data.get('id_tipo_servicio')        # jose
        id_mesa = request.data.get('id_mesa')                          # jose

        # jose: si no envían id_mesero, usar el id del usuario autenticado
        id_mesero = request.data.get('id_mesero')                      # jose
        if id_mesero in (None, "", 0):                                 # jose
            id_mesero = getattr(request.user, "id", None)              # jose

        observaciones = request.data.get('observaciones')

        # -------------------- VALIDACIONES -----------------------------------
        if not id_tipo_servicio:
            return Response({"detail": "id_tipo_servicio es requerido (int)"}, status=400)  # jose

        try:
            TipoServicio.objects.get(pk=id_tipo_servicio)              # jose
        except TipoServicio.DoesNotExist:                               # jose
            return Response({"detail": "id_tipo_servicio no existe"}, status=400)  # jose

        if id_mesa:
            if not Mesa.objects.filter(pk=id_mesa).exists():           # jose
                return Response({"detail": "id_mesa no existe"}, status=400)  # jose

        try:
            estado_abierta = EstadoOrden.objects.get(nombre='ABIERTA')  # jose
        except EstadoOrden.DoesNotExist:                                 # jose
            return Response({"detail": "Estado 'ABIERTA' no existe en EstadoOrden"}, status=400)  # jose

        # ----------------------- INSERT (SQL crudo) ---------------------------
        # jose: tu tabla tiene triggers y columnas calculadas; evitamos OUTPUT y
        # jamás incluimos total/subtotal/descuento en el INSERT.
        fecha = timezone.now()  # jose
        sql = """
        SET NOCOUNT ON;  -- jose: evita contaminar el fetch con rowcounts
        INSERT INTO pos.Orden (fecha_hora, id_mesa, id_mesero, id_estado, id_tipo_servicio, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s);
        SELECT CAST(SCOPE_IDENTITY() AS int);
        """  # jose

        params = [  # jose
            fecha,
            id_mesa,                               # puede ser NULL
            id_mesero,
            estado_abierta.id_estado,
            id_tipo_servicio,
            observaciones,
        ]  # jose

        try:
            with connection.cursor() as cur:       # jose
                cur.execute(sql, params)           # jose
                row = cur.fetchone()               # jose
                new_id = row[0] if row else None   # jose
        except Exception as e:
            return Response(
                {"detail": "Error al crear la orden (SQL)", "error": str(e)}, status=500
            )  # jose

        if not new_id:  # jose
            return Response({"detail": "No se pudo obtener el id de la orden"}, status=500)  # jose

        o = Orden.objects.get(pk=new_id)           # jose
        return Response(self.get_serializer(o).data, status=201)  # jose


    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='agregar-detalle')
    def agregar_detalle(self, request, pk=None):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: { id_producto, cantidad, precio_unitario, nota,
                modificadores?: [{id_modificador, cantidad, precio_extra}] }
        """
        campos = ('id_producto', 'cantidad', 'precio_unitario')
        if any(request.data.get(c) in (None, '') for c in campos):
            return Response({"detail": "id_producto, cantidad y precio_unitario son requeridos"}, status=400)

        o = Orden.objects.get(pk=pk)
        d = OrdenDetalle.objects.create(
            id_orden=o,
            id_producto=request.data['id_producto'],
            cantidad=request.data['cantidad'],
            precio_unitario=request.data['precio_unitario'],
            nota=request.data.get('nota')
        )
        # modificadores opcionales
        for m in request.data.get('modificadores', []):
            OrdenDetalleModificador.objects.create(
                id_detalle=d,
                id_modificador=m['id_modificador'],
                cantidad=m.get('cantidad', 1),
                precio_extra=m.get('precio_extra', 0)
            )
        return Response(OrdenDetalleSerializer(d).data, status=201)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='editar-detalle')
    def editar_detalle(self, request, pk=None):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: { id_detalle, cantidad?, precio_unitario?, nota?,
                modificadores?: { replace: bool, items: [{id_modificador, cantidad?, precio_extra?}] } }
        """
        id_detalle = request.data.get('id_detalle')
        if not id_detalle:
            return Response({"detail": "id_detalle es requerido"}, status=400)

        d = OrdenDetalle.objects.get(pk=id_detalle, id_orden_id=pk)

        # actualizar campos básicos si vienen
        for campo in ['cantidad', 'precio_unitario', 'nota']:
            if campo in request.data:
                setattr(d, campo, request.data[campo])
        # jose: por si hay columnas calculadas en detalle, limita columnas a guardar:
        d.save(update_fields=[c for c in ['cantidad', 'precio_unitario', 'nota'] if c in request.data])  # jose

        mods_payload = request.data.get('modificadores')
        if mods_payload:
            replace = mods_payload.get('replace', False)
            items = mods_payload.get('items', [])
            if replace:
                OrdenDetalleModificador.objects.filter(id_detalle=d).delete()
            for m in items:
                # upsert simple
                OrdenDetalleModificador.objects.update_or_create(
                    id_detalle=d, id_modificador=m['id_modificador'],
                    defaults={
                        'cantidad': m.get('cantidad', 1),
                        'precio_extra': m.get('precio_extra', 0)
                    }
                )
        return Response(OrdenDetalleSerializer(d).data, status=200)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='eliminar-detalle')
    def eliminar_detalle(self, request, pk=None):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: { id_detalle }
        """
        id_detalle = request.data.get('id_detalle')
        if not id_detalle:
            return Response({"detail": "id_detalle es requerido"}, status=400)
        deleted, _ = OrdenDetalle.objects.filter(id_orden_id=pk, id_detalle=id_detalle).delete()
        if not deleted:
            return Response({"detail": "Detalle no encontrado"}, status=404)
        return Response(status=204)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='aplicar-descuento')
    def aplicar_descuento(self, request, pk=None):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: { descuento }
        """
        desc = request.data.get('descuento')
        if desc is None:
            return Response({"detail": "descuento es requerido"}, status=400)

        # jose: limitar UPDATE a la columna editable para no tocar calculadas
        updated = Orden.objects.filter(pk=pk).update(descuento=desc)  # jose
        if not updated:  # jose
            return Response({"detail": "Orden no encontrada"}, status=404)  # jose

        o = Orden.objects.get(pk=pk)  # jose
        return Response(self.get_serializer(o).data, status=200)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        _require_role(request, ORDER_ROLES)  # jose
        """
        body: { id_estado }
        (La lógica de máquina de estados se puede reforzar aquí si lo deseas)
        """
        id_estado = request.data.get('id_estado')
        if not id_estado:
            return Response({"detail": "id_estado es requerido"}, status=400)

        # jose: actualizar SOLO la columna de estado (evita tocar total/subtotal calculados)
        updated = Orden.objects.filter(pk=pk).update(id_estado_id=id_estado)  # jose
        if not updated:  # jose
            return Response({"detail": "Orden no encontrada"}, status=404)  # jose

        o = Orden.objects.get(pk=pk)  # jose
        return Response(self.get_serializer(o).data, status=200)

    # --- NUEVO: cerrar orden (marca como COBRADA) ---
    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        _require_role(request, ORDER_ROLES)

        # Usamos el estado existente en tu BD; si faltara en otra base, lo crea.
        try:
            estado_cobrada = EstadoOrden.objects.get(nombre='COBRADA')
        except EstadoOrden.DoesNotExist:
            estado_cobrada, _ = EstadoOrden.objects.get_or_create(
                nombre='COBRADA', defaults={'nombre': 'COBRADA'}
            )

        # Igual que cambiar_estado: sólo toca la FK (no recalcula totales aquí)
        updated = Orden.objects.filter(pk=pk).update(id_estado_id=estado_cobrada.id_estado)
        if not updated:
            return Response({"detail": "Orden no encontrada"}, status=404)

        o = Orden.objects.get(pk=pk)
        return Response(self.get_serializer(o).data, status=200)
