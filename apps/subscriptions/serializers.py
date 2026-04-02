from rest_framework import serializers
from .models import Plan, Subscription, Invoice, PaymentMethod, UsageRecord

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ['stripe_price_id']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = PlanSerializer(source='plan', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    days_until_renewal = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['organization', 'stripe_subscription_id']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['organization', 'invoice_number', 'stripe_invoice_id']

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ['user', 'stripe_payment_method_id']

class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = '__all__'
