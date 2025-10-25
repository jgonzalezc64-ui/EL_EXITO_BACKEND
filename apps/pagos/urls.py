from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetodoPagoViewSet, PagoViewSet

router = DefaultRouter()
router.register(r'metodos', MetodoPagoViewSet, basename='metodo-pago')
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [ path('', include(router.urls)) ]
