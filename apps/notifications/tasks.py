from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.notifications.services import NotificationService
from apps.subscriptions.models import Subscription

@shared_task
def check_trial_ending_notifications():
    """Envoyer des notifications pour les essais qui se terminent"""
    # Essais qui se terminent dans 3 jours
    soon = timezone.now() + timedelta(days=3)
    trials_ending = Subscription.objects.filter(
        status='trialing',
        trial_end__lte=soon
    )

    for subscription in trials_ending:
        days_left = (subscription.trial_end - timezone.now()).days

        NotificationService.send_notification(
            user_id=subscription.user.id,
            title=f"Votre essai se termine dans {days_left} jours",
            message=f"Votre essai {subscription.plan.name} se termine bientôt. Pensez à vous abonner pour continuer à profiter de nos services.",
            notification_type='warning',
            organization=subscription.organization
        )

@shared_task
def check_subscription_renewal():
    """Vérifier les renouvellements d'abonnements"""
    # Abonnements qui se renouvellent dans 7 jours
    renewing_soon = Subscription.objects.filter(
        status='active',
        current_period_end__lte=timezone.now() + timedelta(days=7)
    )

    for subscription in renewing_soon:
        NotificationService.send_notification(
            user_id=subscription.user.id,
            title="Votre abonnement va être renouvelé",
            message=f"Votre abonnement {subscription.plan.name} sera renouvelé le {subscription.current_period_end.strftime('%d/%m/%Y')}. Montant: {subscription.amount} {subscription.currency}",
            notification_type='info',
            organization=subscription.organization
        )

@shared_task
def send_daily_digest():
    """Envoyer le digest quotidien des notifications"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Users qui veulent un digest quotidien
    from apps.notifications.models import NotificationPreference
    users_for_digest = NotificationPreference.objects.filter(
        digest_frequency='daily'
    )

    for pref in users_for_digest:
        # Récupérer les notifications non lues des 24 dernières heures
        from apps.notifications.models import Notification
        yesterday = timezone.now() - timedelta(days=1)

        unread_notifications = Notification.objects.filter(
            user=pref.user,
            created_at__gte=yesterday,
            is_read=False
        ).count()

        if unread_notifications > 0:
            NotificationService.send_notification(
                user_id=pref.user.id,
                title="Votre digest quotidien",
                message=f"Vous avez {unread_notifications} nouvelles notifications.",
                notification_type='info'
            )

@shared_task
def cleanup_old_notifications():
    """Nettoyer les anciennes notifications lues"""
    from datetime import timedelta
    from apps.notifications.models import Notification

    # Supprimer les notifications lues de plus de 30 jours
    cutoff = timezone.now() - timedelta(days=30)
    old_notifications = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff
    ).delete()

    return f"Deleted {old_notifications[0]} old notifications"
