from django.contrib import admin
from .models import Plan, Subscription, Invoice, PaymentMethod, UsageRecord

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'billing_cycle', 'trial_days', 'is_active', 'is_popular']
    list_filter = ['billing_cycle', 'is_active', 'is_popular']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'current_period_end', 'is_active']
    list_filter = ['status', 'plan']
    search_fields = ['organization__name', 'user__email']
    date_hierarchy = 'created_at'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'total', 'status', 'due_date', 'paid_at']
    list_filter = ['status', 'due_date']
    search_fields = ['invoice_number', 'organization__name']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'card_last4', 'is_default']
    list_filter = ['payment_type', 'is_default']
    search_fields = ['user__email']

@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'metric_name', 'quantity', 'amount', 'recorded_at']
    list_filter = ['metric_name', 'recorded_at']
    date_hierarchy = 'recorded_at'
