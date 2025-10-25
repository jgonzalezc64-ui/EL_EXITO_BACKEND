from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, MenuSeccionViewSet, MenuItemViewSet

router = DefaultRouter()
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'secciones', MenuSeccionViewSet, basename='menu-seccion')
router.register(r'items', MenuItemViewSet, basename='menu-item')

urlpatterns = [ path('', include(router.urls)) ]
