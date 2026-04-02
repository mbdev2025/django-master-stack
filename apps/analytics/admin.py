from django.contrib import admin
from .models import Event, Metric, DailyStats, Funnel, Report

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'event_type', 'organization', 'user', 'created_at']
    list_filter = ['event_type', 'created_at', 'organization']
    search_fields = ['event_name', 'session_id', 'user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'metric_type', 'organization', 'date', 'hour']
    list_filter = ['metric_type', 'date', 'organization']
    search_fields = ['metric_name']
    date_hierarchy = 'date'

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['organization', 'date', 'new_users', 'active_users', 'page_views', 'revenue']
    list_filter = ['date', 'organization']
    date_hierarchy = 'date'
    readonly_fields = ['date']

    def has_add_permission(self, request):
        return False  # Calculé automatiquement

@admin.register(Funnel)
class FunnelAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'total_entries', 'conversion_rate', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'report_type', 'is_scheduled', 'created_at']
    list_filter = ['report_type', 'is_scheduled', 'organization']
    search_fields = ['name', 'description']
