from django.urls import path
from .views import automation_list

urlpatterns = [
    path('automations/', automation_list, name='automation-list'),
]
