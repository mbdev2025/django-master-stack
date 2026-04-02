from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlanViewSet, SubscriptionViewSet, InvoiceViewSet,
    PaymentMethodViewSet, UsageRecordViewSet
)

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='subscription-plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'usage', UsageRecordViewSet, basename='usage-record')

urlpatterns = [
    path('', include(router.urls)),
]
