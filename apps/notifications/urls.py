from django.urls import path
from .views import notification_list

urlpatterns = [
    path('notifications/', notification_list, name='notification-list'),
]
