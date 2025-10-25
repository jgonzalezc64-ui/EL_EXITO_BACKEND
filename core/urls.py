from django.contrib import admin
from django.urls import path, include

# --- jose: importar vistas de SimpleJWT ---
from rest_framework_simplejwt.views import (  # jose
    TokenObtainPairView,                      # jose
    TokenRefreshView,                         # jose
)                                             # jose

urlpatterns = [
    path('admin/', admin.site.urls),
    # Reservamos el prefijo de API (las apps se irán conectando aquí)
    path('api/v1/', include([])),  # lo iremos poblando en el PASO 6–8

    # --- jose: endpoints de autenticación JWT (login/refresh) ---
    path('api/v1/auth/jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # jose
    path('api/v1/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),        # jose

    path('api/v1/catalogos/', include('apps.catalogos.urls')),
    path('api/v1/pedidos/', include('apps.pedidos.urls')),
    path('api/v1/pagos/', include('apps.pagos.urls')),
    path('api/v1/kds/', include('apps.kds.urls')),
    path('api/v1/menus/', include('apps.menus.urls')),
    path('api/v1/seguridad/', include('apps.seguridad.urls')),
]
