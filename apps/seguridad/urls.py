from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, RefreshView, MeViewSet,
    UserViewSet, GroupViewSet,
    RolPOSViewSet, UsuarioPOSViewSet
)

router = DefaultRouter()
router.register(r'me', MeViewSet, basename='me')
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')

# opcional POS
router.register(r'pos/roles', RolPOSViewSet, basename='pos-rol')
router.register(r'pos/usuarios', UsuarioPOSViewSet, basename='pos-usuario')

urlpatterns = [
    path('auth/login',  LoginView.as_view(),   name='token_obtain_pair'),
    path('auth/refresh', RefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
