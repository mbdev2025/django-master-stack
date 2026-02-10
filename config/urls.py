from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # === Authentication (Mobile JWT) ===
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # === Documentation (Swagger) ===
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # === Apps ===
    # path('api/payments/', include('apps.payments.urls')),
    # path('api/automation/', include('apps.automation.urls')),

    # === CMS (Wagtail) ===
    path('cms/', include(wagtailadmin_urls)),
    path('', include(wagtail_urls)), # Must be last!
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
