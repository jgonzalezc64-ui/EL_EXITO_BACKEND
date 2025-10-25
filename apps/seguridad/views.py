from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    UserSerializer, UserCreateSerializer, GroupSerializer
)
# opcional POS
from .models import RolPOS, UsuarioPOS
from .serializers import RolPOSSerializer, UsuarioPOSSerializer

# --- Auth (JWT) ---
class LoginView(TokenObtainPairView):
    """POST /seguridad/auth/login -> {access, refresh}"""

class RefreshView(TokenRefreshView):
    """POST /seguridad/auth/refresh -> {access}"""

# --- Yo (perfil) ---
class MeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        u = request.user
        groups = list(u.groups.values_list("name", flat=True))
        # Respuesta mínima necesaria para el front:
        data = {
            "id": u.id,
            "username": u.username,
            "is_superuser": bool(u.is_superuser),
            "groups": groups,
            # Campos extra opcionales; no rompen nada en el front:
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
        }
        return Response(data)

# --- Usuarios (CRUD admin) ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    permission_classes = [IsAdminUser]  # Solo admin
    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']:
            return UserCreateSerializer
        return UserSerializer

# --- Roles/Grupos (CRUD admin) ---
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

# --- POS lectura opcional ---
class RolPOSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RolPOS.objects.all().order_by('nombre')
    serializer_class = RolPOSSerializer
    permission_classes = [permissions.AllowAny]

class UsuarioPOSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UsuarioPOS.objects.select_related('id_rol').all().order_by('-fecha_creacion')
    serializer_class = UsuarioPOSSerializer
    permission_classes = [permissions.AllowAny]
