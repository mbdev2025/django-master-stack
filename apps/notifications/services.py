from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Notification, NotificationPreference, NotificationLog

class NotificationService:
    """Service pour gérer les notifications"""

    @staticmethod
    def send_notification(user_id, title, message, notification_type='info', organization=None, data=None):
        """Envoyer une notification in-app"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)

            notification = Notification.objects.create(
                user=user,
                organization=organization,
                notification_type=notification_type,
                title=title,
                message=message,
                data=data or {}
            )

            # Envoyer les notifications selon les préférences
            preferences = NotificationService._get_or_create_preferences(user)

            if preferences.inapp_notifications_enabled:
                # Notification in-app déjà créée
                pass

            if preferences.email_notifications_enabled:
                NotificationService._send_email_notification(notification, preferences)

            if preferences.push_notifications_enabled:
                NotificationService._send_push_notification(notification)

            return notification

        except User.DoesNotExist:
            raise Exception("User not found")

    @staticmethod
    def _get_or_create_preferences(user):
        """Récupérer ou créer les préférences de notification"""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user
        )
        return preferences

    @staticmethod
    def _send_email_notification(notification, preferences):
        """Envoyer la notification par email"""
        try:
            # Vérifier si on est dans les heures calme
            if NotificationService._is_quiet_hours(preferences):
                return

            # Récupérer le template email
            # TODO: implémenter les templates personnalisés
            subject = f"[{notification.organization.name if notification.organization else 'System'}] {notification.title}"

            message = f"""
            Bonjour {notification.user.get_full_name()},

            {notification.message}

            ---
            Pour plus de détails, connectez-vous à votre espace.
            """

            # Envoyer l'email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [notification.user.email],
                fail_silently=True
            )

            # Logger la notification
            NotificationLog.objects.create(
                notification=notification,
                channel='email',
                recipient=notification.user.email,
                status='sent',
                sent_at=timezone.now()
            )

        except Exception as e:
            # Logger l'erreur
            NotificationLog.objects.create(
                notification=notification,
                channel='email',
                recipient=notification.user.email,
                status='failed',
                error_message=str(e)
            )

    @staticmethod
    def _send_push_notification(notification):
        """Envoyer une notification push"""
        # TODO: implémenter les notifications push (Firebase, OneSignal, etc.)
        pass

    @staticmethod
    def _is_quiet_hours(preferences):
        """Vérifier si on est dans les heures calme"""
        if not preferences.quiet_hours_enabled:
            return False

        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False

        now = timezone.now().time()
        return preferences.quiet_hours_start <= now <= preferences.quiet_hours_end

    @staticmethod
    def send_bulk_notification(user_ids, title, message, notification_type='info'):
        """Envoyer une notification en masse à plusieurs utilisateurs"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        users = User.objects.filter(id__in=user_ids)
        notifications = []

        for user in users:
            try:
                notification = NotificationService.send_notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    notification_type=notification_type
                )
                notifications.append(notification)
            except Exception as e:
                print(f"Error sending notification to {user.email}: {e}")

        return notifications

    @staticmethod
    def create_system_notification(title, message, organization=None):
        """Créer une notification système pour tous les membres d'une organization"""
        if organization:
            from apps.tenants.models import Member
            members = Member.objects.filter(organization=organization, is_active=True)

            for member in members:
                NotificationService.send_notification(
                    user_id=member.user.id,
                    title=title,
                    message=message,
                    notification_type='system',
                    organization=organization
                )
