from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from apps.energy.views import client_dashboard, landing, pro_landing, client_login, client_signup, demo_login
from apps.energy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/energy/', include('apps.energy.urls')),
    

    # Dashboard Routes (Frontend)
    path('dashboard/client/', client_dashboard, name='dashboard-client'),
    path('login/client/', client_login, name='client-login'),
    path('signup/client/', client_signup, name='client-signup'),
    path('dashboard/pro/', TemplateView.as_view(template_name='dashboard/pro.html'), name='dashboard-pro'),
    path('pro/', pro_landing, name='pro-landing'),
    path('demo/login/', demo_login, name='demo_login'),
    path('dashboard/simulation/', TemplateView.as_view(template_name='dashboard/simulation.html'), name='dashboard-simulation'),
    path('dashboard/audit/', include('apps.audit.urls')),
    path('dashboard/analysis/', include('apps.analysis.urls')),
    
    # Simulation Routes (For Pro Demo)
    path('simulation/enedis/authorize/', views.enedis_consent_view, name='simulation_enedis_consent'),
    path('simulation/enedis/success/', TemplateView.as_view(template_name='simulation/enedis_success.html'), name='simulation_enedis_success'),
    path('', landing, name='landing'), # Default to landing page
]
