from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='landing'),

    # API routes
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.tenants.urls')),
    path('api/', include('apps.subscriptions.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.automation.urls')),
]
