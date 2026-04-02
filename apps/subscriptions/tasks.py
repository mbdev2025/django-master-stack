from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.subscriptions.models import Subscription, Invoice
from apps.subscriptions.services import SubscriptionService

@shared_task
def check_trial_ending():
    """Vérifier les essais qui se terminent bientôt"""
    # Essais qui se terminent dans 3 jours
    soon = timezone.now() + timedelta(days=3)
    trials_ending = Subscription.objects.filter(
        status='trialing',
        trial_end__lte=soon
    )

    for subscription in trials_ending:
        # Envoyer notification
        # TODO: implémenter la notification
        pass

@shared_task
def generate_invoices():
    """Générer les factures pour les abonnements actifs"""
    for subscription in Subscription.objects.filter(status='active'):
        try:
            if subscription.current_period_end <= timezone.now():
                invoice = SubscriptionService.create_invoice(subscription)
                # Finaliser la facture Stripe
                # TODO: implémenter la finalisation
        except Exception as e:
            print(f"Error generating invoice for subscription {subscription.id}: {e}")

@shared_task
def check_overdue_subscriptions():
    """Vérifier les abonnements en retard"""
    from datetime import timedelta

    grace_period = timezone.now() - timedelta(days=7)
    overdue = Subscription.objects.filter(
        current_period_end__lt=grace_period,
        status='active'
    )

    for subscription in overdue:
        # Marquer comme past_due
        subscription.status = 'past_due'
        subscription.save()

        # Envoyer notification
        # TODO: implémenter la notification
        pass

@shared_task
def calculate_usage_metrics():
    """Calculer les métriques d'usage pour tous les abonnements"""
    for subscription in Subscription.objects.filter(status='active'):
        try:
            # Calculer l'usage du mois courant
            # TODO: implémenter le calcul d'usage
            pass
        except Exception as e:
            print(f"Error calculating usage for subscription {subscription.id}: {e}")
