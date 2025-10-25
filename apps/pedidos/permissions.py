# jose: NUEVO archivo de permisos para Pedidos
from rest_framework.permissions import BasePermission, SAFE_METHODS

ALLOWED_ORDER_ROLES = ['ADMIN', 'MESERO', 'CAJA']  # jose

class CanOrder(BasePermission):
    """Permite acceso solo a ADMIN/MESERO/CAJA para vistas de órdenes."""  # jose
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated) and
            request.user.groups.filter(name__in=ALLOWED_ORDER_ROLES).exists()
        )  # jose

class IsAdminOrReadOnlyForPedidos(BasePermission):
    """
    Lectura (GET/HEAD/OPTIONS) para ADMIN/MESERO/CAJA; escritura solo ADMIN.
    Útil para Tiendas/Mesas/Estados/Tipos.                           # jose
    """
    def has_permission(self, request, view):
        u = request.user
        if request.method in SAFE_METHODS:
            return bool(u and u.is_authenticated and
                        u.groups.filter(name__in=ALLOWED_ORDER_ROLES).exists())  # jose
        return bool(u and u.is_authenticated and
                    u.groups.filter(name='ADMIN').exists())  # jose
