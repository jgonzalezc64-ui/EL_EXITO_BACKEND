# jose
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from apps.pedidos.models import Orden, EstadoOrden  # jose
from apps.pedidos.serializers import OrdenSerializer  # jose

def _require_role(request, allowed_groups):  # jose
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    if getattr(request.user, "is_superuser", False):
        return
    # por Group
    if request.user.groups.filter(name__in=allowed_groups).exists():
        return
    # por id_rol de tu BD (3 = COCINA)
    if getattr(request.user, 'id_rol', None) in (3,):
        return
    raise PermissionDenied("No tiene permisos para esta acción")

KDS_ROLES = ['COCINA']  # jose

class KDSOrdenViewSet(viewsets.GenericViewSet):  # jose
    permission_classes = [IsAuthenticated]       # jose
    serializer_class = OrdenSerializer           # jose

    def get_queryset(self):
        return (
            Orden.objects
            .select_related('id_estado', 'id_tipo_servicio', 'id_mesa')
            .filter(id_estado__nombre='EN_COCINA')     # jose
            .order_by('fecha_hora', 'id_orden')
        )

    def list(self, request, *args, **kwargs):
        _require_role(request, KDS_ROLES)  # jose
        ser = self.get_serializer(self.get_queryset(), many=True)
        return Response(ser.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        _require_role(request, KDS_ROLES)  # jose
        o = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(o).data)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='marcar-lista')  # jose
    def marcar_lista(self, request, pk=None):
        _require_role(request, KDS_ROLES)  # jose
        try:
            estado_lista = EstadoOrden.objects.get(nombre='LISTA')  # jose
        except EstadoOrden.DoesNotExist:
            return Response({"detail": "Estado 'LISTA' no existe en EstadoOrden"}, status=400)

        updated = (
            Orden.objects
            .filter(pk=pk, id_estado__nombre='EN_COCINA')
            .update(id_estado_id=estado_lista.id_estado)
        )  # jose

        if not updated:
            return Response({"detail": "Orden no encontrada o no está en cocina"}, status=404)  # jose

        o = Orden.objects.get(pk=pk)  # jose
        return Response(self.get_serializer(o).data, status=200)  # jose
