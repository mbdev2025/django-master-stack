from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import Event, Metric, DailyStats, Funnel, Report
from .serializers import (
    EventSerializer, MetricSerializer, DailyStatsSerializer,
    FunnelSerializer, ReportSerializer
)
from .services import AnalyticsService

class EventViewSet(viewsets.ModelViewSet):
    """ViewSet pour les événements"""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(
            organization__members__user=user
        ).select_related('user')

    def perform_create(self, serializer):
        # Auto-assign organization from user
        org = self.request.user.organization_memberships.first().organization
        serializer.save(organization=org)

    @action(detail=False, methods=['post'])
    def track(self, request):
        """Tracker un événement depuis le frontend"""
        try:
            AnalyticsService.track_event(
                organization=request.user.organization_memberships.first().organization,
                event_type=request.data.get('event_type', 'custom'),
                event_name=request.data.get('event_name'),
                user=request.user,
                session_id=request.data.get('session_id'),
                properties=request.data.get('properties', {}),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
            return Response({'status': 'tracked'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MetricViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les métriques"""
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Metric.objects.filter(
            organization__members__user=user
        )

class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les statistiques quotidiennes"""
    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return DailyStats.objects.filter(
            organization__members__user=user
        ).order_by('-date')

    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """Statistiques temps réel"""
        minutes = int(request.query_params.get('minutes', 30))
        org = request.user.organization_memberships.first().organization

        stats = AnalyticsService.get_realtime_stats(org, minutes)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def traffic_sources(self, request):
        """Sources de trafic"""
        days = int(request.query_params.get('days', 7))
        org = request.user.organization_memberships.first().organization

        sources = AnalyticsService.get_traffic_sources(org, days)
        return Response(sources)

    @action(detail=False, methods=['get'])
    def top_pages(self, request):
        """Pages les plus visitées"""
        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 10))
        org = request.user.organization_memberships.first().organization

        pages = AnalyticsService.get_top_pages(org, days, limit)
        return Response(pages)

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Revenu dans le temps"""
        days = int(request.query_params.get('days', 30))
        org = request.user.organization_memberships.first().organization

        revenue = AnalyticsService.get_revenue_over_time(org, days)
        return Response(revenue)

class FunnelViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tunnels de conversion"""
    serializer_class = FunnelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Funnel.objects.filter(
            organization__members__user=user
        )

    @action(detail=True, methods=['get'])
    def analyze(self, request, pk=None):
        """Analyser un tunnel"""
        days = int(request.query_params.get('days', 7))
        funnel = self.get_object()

        funnel_data = AnalyticsService.get_conversion_funnel(
            funnel.organization,
            funnel.steps,
            days
        )

        return Response(funnel_data)

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet pour les rapports"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Report.objects.filter(
            organization__members__user=user
        )
