from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from django.core.cache import cache
from .models import Event, DailyStats, Metric

class AnalyticsService:
    """Service pour calculer les analytics"""

    @staticmethod
    def track_event(organization, event_type, event_name, user=None, session_id=None, properties=None, **kwargs):
        """Enregistrer un événement"""
        Event.objects.create(
            organization=organization,
            event_type=event_type,
            event_name=event_name,
            user=user,
            session_id=session_id or AnalyticsService._generate_session_id(),
            properties=properties or {},
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            referrer=kwargs.get('referrer')
        )

    @staticmethod
    def _generate_session_id():
        """Générer un session ID unique"""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def calculate_daily_stats(organization, date=None):
        """Calculer les statistiques quotidiennes"""
        if date is None:
            date = timezone.now().date()

        # Calculer les métriques
        events = Event.objects.filter(
            organization=organization,
            created_at__date=date
        )

        # Users
        new_users = events.filter(event_type='signup').values('user').distinct().count()
        active_users = events.values('user').distinct().count()
        returning_users = events.filter(
            event_type='login'
        ).exclude(
            created_at__date=date
        ).values('user').distinct().count()

        # Sessions
        total_sessions = events.values('session_id').distinct().count()

        # Page Views
        page_views = events.filter(event_type='page_view').count()
        unique_page_views = events.filter(
            event_type='page_view'
        ).values('properties__page').distinct().count()

        # Conversions
        signups = events.filter(event_type='signup').count()
        purchases = events.filter(event_type='purchase').count()
        subscriptions = events.filter(event_type='subscription').count()

        # Revenue
        revenue = events.filter(
            event_type='purchase'
        ).aggregate(
            total=Sum(F('properties__value__amount'))
        )['total'] or 0

        # Créer ou mettre à jour
        stats, created = DailyStats.objects.get_or_create(
            organization=organization,
            date=date,
            defaults={
                'new_users': new_users,
                'active_users': active_users,
                'returning_users': returning_users,
                'total_sessions': total_sessions,
                'page_views': page_views,
                'unique_page_views': unique_page_views,
                'signups': signups,
                'purchases': purchases,
                'subscriptions': subscriptions,
                'revenue': revenue,
            }
        )

        if not created:
            # Update si existe déjà
            stats.new_users = new_users
            stats.active_users = active_users
            stats.returning_users = returning_users
            stats.total_sessions = total_sessions
            stats.page_views = page_views
            stats.unique_page_views = unique_page_views
            stats.signups = signups
            stats.purchases = purchases
            stats.subscriptions = subscriptions
            stats.revenue = revenue
            stats.save()

        return stats

    @staticmethod
    def get_realtime_stats(organization, minutes=30):
        """Statistiques temps réel"""
        since = timezone.now() - timedelta(minutes=minutes)

        events = Event.objects.filter(
            organization=organization,
            created_at__gte=since
        )

        return {
            'page_views': events.filter(event_type='page_view').count(),
            'unique_visitors': events.values('session_id').distinct().count(),
            'active_users': events.values('user').distinct().count(),
            'signups': events.filter(event_type='signup').count(),
            'purchases': events.filter(event_type='purchase').count(),
        }

    @staticmethod
    def get_traffic_sources(organization, days=7):
        """Sources de trafic"""
        since = timezone.now() - timedelta(days=days)

        events = Event.objects.filter(
            organization=organization,
            created_at__gte=since,
            event_type='page_view'
        )

        sources = {}
        for event in events:
            referrer = event.referrer or 'Direct'
            sources[referrer] = sources.get(referrer, 0) + 1

        return sorted(sources.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def get_top_pages(organization, days=7, limit=10):
        """Pages les plus visitées"""
        since = timezone.now() - timedelta(days=days)

        from django.db.models import Func

        events = Event.objects.filter(
            organization=organization,
            created_at__gte=since,
            event_type='page_view'
        )

        # Extraire le path depuis properties
        pages = {}
        for event in events:
            page = event.properties.get('page', 'unknown')
            pages[page] = pages.get(page, 0) + 1

        return sorted(pages.items(), key=lambda x: x[1], reverse=True)[:limit]

    @staticmethod
    def get_conversion_funnel(organization, steps, days=7):
        """Calculer un tunnel de conversion"""
        since = timezone.now() - timedelta(days=days)

        funnel_data = []
        total = Event.objects.filter(
            organization=organization,
            created_at__gte=since
        ).count()

        for step in steps:
            count = Event.objects.filter(
                organization=organization,
                created_at__gte=since,
                event_name=step
            ).count()

            funnel_data.append({
                'step': step,
                'count': count,
                'percentage': (count / total * 100) if total > 0 else 0
            })

        return funnel_data

    @staticmethod
    def get_user_retention(organization, days=30):
        """Analyse de rétention utilisateurs"""
        from apps.users.models import User

        # Users créés dans la période
        since = timezone.now() - timedelta(days=days)
        new_users = User.objects.filter(
            date_joined__gte=since,
            organization_memberships__organization=organization
        )

        retention_data = {}
        for user in new_users:
            # Calculer la dernière activité
            last_event = Event.objects.filter(
                user=user
            ).order_by('-created_at').first()

            if last_event:
                days_since_last = (timezone.now() - last_event.created_at).days
                retention_data[days_since_last] = retention_data.get(days_since_last, 0) + 1

        return retention_data

    @staticmethod
    def get_revenue_over_time(organization, days=30):
        """Revenu dans le temps"""
        since = timezone.now() - timedelta(days=days)

        from django.db.models import Sum

        events = Event.objects.filter(
            organization=organization,
            created_at__gte=since,
            event_type='purchase'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum(F('properties__value__amount'))
        ).order_by('date')

        return list(events)

    @staticmethod
    def cache_key_stats(organization_id):
        """Clé de cache pour les stats"""
        return f'analytics:stats:{organization_id}'

    @staticmethod
    def get_cached_stats(organization):
        """Récupérer les stats depuis le cache"""
        cache_key = AnalyticsService.cache_key_stats(organization.id)
        stats = cache.get(cache_key)

        if stats is None:
            # Calculer et mettre en cache
            stats = AnalyticsService.calculate_daily_stats(organization)
            cache.set(cache_key, stats, timeout=3600)  # 1 heure

        return stats
