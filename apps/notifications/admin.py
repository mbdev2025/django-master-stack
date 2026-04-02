from django.contrib import admin
from .models import Notification, NotificationPreference, EmailTemplate, NotificationLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications_enabled', 'push_notifications_enabled', 'digest_frequency']
    list_filter = ['email_notifications_enabled', 'push_notifications_enabled', 'digest_frequency']
    search_fields = ['user__email']

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['organization', 'template_key', 'name', 'is_active']
    list_filter = ['organization', 'is_active']
    search_fields = ['organization__name', 'template_key', 'name']

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['channel', 'recipient', 'status', 'sent_at', 'delivered_at']
    list_filter = ['channel', 'status']
    search_fields = ['recipient', 'provider_message_id']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
