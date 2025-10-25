# apps/pedidos/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TiendaViewSet,
    MesaViewSet,
    EstadoOrdenViewSet,
    TipoServicioViewSet,
    OrdenViewSet,
)

# jose: usar app_name para permitir namespacing (include('pedidos.urls', namespace='pedidos'))
app_name = "pedidos"  # jose

# jose: explicitamos trailing_slash=True 
router = DefaultRouter(trailing_slash=True)  # jose

# Endpoints REST (viewsets)
router.register(r"tiendas", TiendaViewSet, basename="tienda")
router.register(r"mesas", MesaViewSet, basename="mesa")
router.register(r"estados-orden", EstadoOrdenViewSet, basename="estado-orden")
router.register(r"tipos-servicio", TipoServicioViewSet, basename="tipo-servicio")
router.register(r"ordenes", OrdenViewSet, basename="orden")

# jose: exponemos todas las rutas del router
urlpatterns = [
    path("", include(router.urls)),  # jose
    path('admin/', include('apps.pedidos.admin_urls')),  # jose: /api/v1/pedidos/admin/…
]
