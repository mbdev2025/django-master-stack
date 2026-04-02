from rest_framework import serializers
from .models import Event, Metric, DailyStats, Funnel, Report

class EventSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organization', 'event_type', 'event_name', 'user',
            'user_email', 'session_id', 'properties', 'created_at'
        ]
        read_only_fields = ['organization', 'created_at']

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = '__all__'
        read_only_fields = ['organization']

class DailyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStats
        fields = '__all__'

class DailyStatsDetailSerializer(DailyStatsSerializer):
    conversion_rate = serializers.SerializerMethodField()

    def get_conversion_rate(self, obj):
        if obj.page_views > 0:
            return round((obj.signups / obj.page_views) * 100, 2)
        return 0

class FunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funnel
        fields = '__all__'
        read_only_fields = ['organization']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['organization']
