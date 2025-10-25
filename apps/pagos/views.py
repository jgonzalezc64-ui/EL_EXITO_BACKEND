from django.utils import timezone
from django.db import connection, transaction
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.seguridad.permissions import IsCaja

from .models import MetodoPago, Pago
from .serializers import MetodoPagoSerializer, PagoSerializer

class MetodoPagoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetodoPago.objects.all().order_by('nombre')
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsCaja]

class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /pagos/?id_orden=123  -> lista pagos de una orden
    POST /pagos/registrar     -> registra un pago y si Σ≥total marca COBRADA
    """
    serializer_class = PagoSerializer
    permission_classes = [IsCaja]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-fecha_hora','-id_pago']

    def get_queryset(self):
        qs = Pago.objects.all().order_by('-fecha_hora','-id_pago')
        id_orden = self.request.query_params.get('id_orden')
        if id_orden:
            qs = qs.filter(id_orden=id_orden)
        return qs

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='registrar',permission_classes=[IsCaja])
    def registrar(self, request):
        """
        body: { id_orden, id_metodo, monto, referencia? }
        Lógica:
        - Inserta pago (fecha_hora = now UTC)
        - Recalcula Σ pagos de la orden y compara contra total (columna calculada)
        - Si Σ >= total y estado != COBRADA -> actualiza estado a COBRADA
        """
        id_orden = request.data.get('id_orden')
        id_metodo = request.data.get('id_metodo')
        monto = request.data.get('monto')
        referencia = request.data.get('referencia')

        if not all([id_orden, id_metodo, monto]):
            return Response({"detail":"id_orden, id_metodo y monto son requeridos."}, status=400)

        # 1) Insertar pago
        pago = Pago.objects.create(
            id_orden=int(id_orden),
            id_metodo=int(id_metodo),
            monto=monto,
            fecha_hora=timezone.now(),
            referencia=referencia
        )

        # 2) Verificar que la orden esté en estado ENTREGADA y calcular totales
        with connection.cursor() as cur:
            # Primero verificamos el estado
            cur.execute("""
                SELECT o.total, o.id_estado, e.nombre as estado
                  FROM pos.Orden o
                  JOIN pos.EstadoOrden e ON o.id_estado = e.id_estado
                 WHERE o.id_orden = %s
            """, [id_orden])
            row = cur.fetchone()
            if not row:
                return Response({"detail":"Orden no existe"}, status=404)
            
            total, id_estado_actual, estado_actual = row
            
            if estado_actual != 'ENTREGADA':
                return Response(
                    {"detail": "La orden debe estar en estado ENTREGADA para procesar el pago"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            cur.execute("""
                SELECT COALESCE(SUM(monto),0)
                  FROM pos.Pago
                 WHERE id_orden = %s
            """, [id_orden])
            suma = cur.fetchone()[0]

            if suma is not None and total is not None and float(suma) >= float(total):
                # obtener id_estado COBRADA
                cur.execute("SELECT id_estado FROM pos.EstadoOrden WHERE nombre = 'COBRADA'")
                cobrada = cur.fetchone()
                if cobrada:
                    cur.execute("""
                       UPDATE pos.Orden SET id_estado = %s WHERE id_orden = %s
                    """, [cobrada[0], id_orden])

        return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)
