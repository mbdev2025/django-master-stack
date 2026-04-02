from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from apps.analytics.services import AnalyticsService
from apps.tenants.models import Organization

@shared_task
def calculate_daily_stats_for_all():
    """Calculer les stats quotidiennes pour toutes les organizations"""
    yesterday = timezone.now().date() - timezone.timedelta(days=1)

    for org in Organization.objects.filter(is_active=True):
        try:
            AnalyticsService.calculate_daily_stats(org, yesterday)
        except Exception as e:
            print(f"Error calculating stats for org {org.id}: {e}")

@shared_task
def calculate_realtime_metrics():
    """Calculer les métriques temps réel et mettre en cache"""
    for org in Organization.objects.filter(is_active=True):
        try:
            stats = AnalyticsService.get_realtime_stats(org, minutes=5)
            cache.set(f'analytics:realtime:{org.id}', stats, timeout=300)  # 5 min
        except Exception as e:
            print(f"Error calculating realtime metrics for org {org.id}: {e}")

@shared_task
def cleanup_old_events(days=90):
    """Nettoyer les anciens événements"""
    from datetime import timedelta
    from apps.analytics.models import Event

    cutoff = timezone.now() - timedelta(days=days)

    # Archiver au lieu de supprimer
    old_events = Event.objects.filter(created_at__lt=cutoff)

    count = old_events.count()
    old_events.delete()  # Ou archiver dans une table d'archive

    return f"Deleted {count} old events"
