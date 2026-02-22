from django.urls import path
from . import views

urlpatterns = [
    path('', views.audit_dashboard, name='audit_dashboard'),
    path('add/', views.add_equipment, name='audit_add_equipment'),
    path('delete/<int:eq_id>/', views.delete_equipment, name='audit_delete_equipment'),
    
    # Quote Management
    path('quote/', views.quote_editor, name='audit_quote_editor'),
    path('quote/add/', views.add_quote_line, name='audit_add_quote_line'),
    path('quote/delete/<int:item_id>/', views.delete_quote_line, name='audit_delete_quote_line'),
    
    # ROI & Report
    path('roi/', views.roi_report, name='audit_roi_report'),
    path('roi/update/', views.update_assumptions, name='audit_update_assumptions'),
]
