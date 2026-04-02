from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, MetricViewSet, DailyStatsViewSet, FunnelViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='analytics-event')
router.register(r'metrics', MetricViewSet, basename='analytics-metric')
router.register(r'daily-stats', DailyStatsViewSet, basename='analytics-daily-stats')
router.register(r'funnels', FunnelViewSet, basename='analytics-funnel')
router.register(r'reports', ReportViewSet, basename='analytics-report')

urlpatterns = [
    path('', include(router.urls)),
]
