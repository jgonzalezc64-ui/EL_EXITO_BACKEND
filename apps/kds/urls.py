# jose
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KDSOrdenViewSet  # jose

router = DefaultRouter()
router.register(r'ordenes', KDSOrdenViewSet, basename='kds-ordenes')  # jose

urlpatterns = [
    path('', include(router.urls)),
]
