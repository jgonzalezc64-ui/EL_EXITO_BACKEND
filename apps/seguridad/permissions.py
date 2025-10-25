from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInGroup(BasePermission):
    required_groups: list[str] = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_groups = set(request.user.groups.values_list('name', flat=True))
        return any(g in user_groups for g in self.required_groups)

class IsAdmin(IsInGroup):
    required_groups = ['ADMIN']

class IsCaja(IsInGroup):
    required_groups = ['CAJA', 'ADMIN']  # ADMIN también permitido

class IsCocina(IsInGroup):
    required_groups = ['COCINA', 'ADMIN']

class IsMesero(IsInGroup):
    required_groups = ['MESERO', 'ADMIN']

class IsAdminOrReadOnly(BasePermission):
    """Lectura: requiere autenticación (o abre si lo indicas en la vista). Escritura: sólo ADMIN."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='ADMIN').exists()
    
class IsCocinaOrMeseroReadOnly(BasePermission):
    """
    - SAFE_METHODS (GET/HEAD/OPTIONS): COCINA, ADMIN y MESERO pueden ver.
    - Métodos de escritura/acción (POST/PATCH/DELETE): solo COCINA y ADMIN.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        groups = set(user.groups.values_list('name', flat=True))
        if request.method in SAFE_METHODS:
            return bool(groups & {'COCINA', 'ADMIN', 'MESERO'})
        return bool(groups & {'COCINA', 'ADMIN'})
