# apps/pedidos/admin_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import (  # jose
    AdminTiendaViewSet, AdminMesaViewSet,  # jose
    AdminEstadoOrdenViewSet, AdminTipoServicioViewSet  # jose
)

router = DefaultRouter()
router.register(r'tiendas', AdminTiendaViewSet, basename='admin-tienda')  # jose
router.register(r'mesas', AdminMesaViewSet, basename='admin-mesa')  # jose
router.register(r'estados-orden', AdminEstadoOrdenViewSet, basename='admin-estado-orden')  # jose
router.register(r'tipos-servicio', AdminTipoServicioViewSet, basename='admin-tipo-servicio')  # jose

urlpatterns = [
    path('', include(router.urls)),  # jose
]
