from django.urls import path
from .views import subscription_list

urlpatterns = [
    path('subscriptions/', subscription_list, name='subscription-list'),
]
