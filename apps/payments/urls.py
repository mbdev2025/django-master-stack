from django.urls import path
from .views import payment_list

urlpatterns = [
    path('payments/', payment_list, name='payment-list'),
]
