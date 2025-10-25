from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, ProductoViewSet,
    ModificadorGrupoViewSet, ModificadorViewSet,
    ProductoModificadorViewSet
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'modificador-grupos', ModificadorGrupoViewSet, basename='modificador-grupo')
router.register(r'modificadores', ModificadorViewSet, basename='modificador')
router.register(r'producto-modificadores', ProductoModificadorViewSet, basename='producto-modificador')

urlpatterns = [
    path('', include(router.urls)),
]
