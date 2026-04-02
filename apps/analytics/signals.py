from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.analytics.services import AnalyticsService

User = get_user_model()

@receiver(post_save, sender=User)
def track_user_signup(sender, instance, created, **kwargs):
    """Tracker les inscriptions automatiquement"""
    if created:
        try:
            # Récupérer l'organization du user
            membership = instance.organization_memberships.first()
            if membership:
                AnalyticsService.track_event(
                    organization=membership.organization,
                    event_type='signup',
                    event_name='user_registered',
                    user=instance,
                    properties={
                        'user_id': instance.id,
                        'email': instance.email,
                        'role': instance.role
                    }
                )
        except Exception as e:
            print(f"Error tracking signup: {e}")
