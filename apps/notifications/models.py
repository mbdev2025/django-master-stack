from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Notification(models.Model):
    """Notifications pour les utilisateurs"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('system', 'Système'),
    ]

    # User
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('utilisateur')
    )

    # Organization context
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('organisation'),
        null=True,
        blank=True
    )

    # Notification details
    notification_type = models.CharField(
        _('type notification'),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info'
    )
    title = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))

    # Optional data
    data = models.JSONField(_('données'), default=dict, blank=True)
    action_url = models.URLField(_('URL action'), blank=True)
    action_label = models.CharField(_('label action'), max_length=100, blank=True)

    # Status
    is_read = models.BooleanField(_('lu'), default=False)
    read_at = models.DateTimeField(_('lu à'), null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('créé à'), auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(_('expire à'), null=True, blank=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        """Marquer comme lu"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class NotificationPreference(models.Model):
    """Préférences de notification des utilisateurs"""
    # User
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('utilisateur')
    )

    # Email notifications
    email_notifications_enabled = models.BooleanField(
        _('notifications email activées'),
        default=True
    )
    email_on_signup = models.BooleanField(_('email à inscription'), default=True)
    email_on_purchase = models.BooleanField(_('email à achat'), default=True)
    email_on_subscription = models.BooleanField(_('email à abonnement'), default=True)
    email_marketing = models.BooleanField(_('email marketing'), default=False)

    # Push notifications (web/mobile)
    push_notifications_enabled = models.BooleanField(
        _('notifications push activées'),
        default=True
    )

    # SMS notifications
    sms_notifications_enabled = models.BooleanField(
        _('notifications SMS activées'),
        default=False
    )
    sms_on_purchase = models.BooleanField(_('SMS à achat'), default=False)
    sms_on_subscription = models.BooleanField(_('SMS à abonnement'), default=False)

    # In-app notifications
    inapp_notifications_enabled = models.BooleanField(
        _('notifications in-app activées'),
        default=True
    )

    # Digest frequency
    digest_frequency = models.CharField(
        _('fréquence digest'),
        max_length=20,
        choices=[
            ('immediate', 'Immédiat'),
            ('hourly', 'Horaire'),
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('never', 'Jamais'),
        ],
        default='immediate'
    )

    # Quiet hours (ne pas déranger)
    quiet_hours_enabled = models.BooleanField(_('heures calme activées'), default=False)
    quiet_hours_start = models.TimeField(_('début heures calme'), null=True, blank=True)
    quiet_hours_end = models.TimeField(_('fin heures calme'), null=True, blank=True)

    class Meta:
        verbose_name = _('préférence notification')
        verbose_name_plural = _('préférences notifications')
        unique_together = ['user']

    def __str__(self):
        return f"Préférences - {self.user.email}"

class EmailTemplate(models.Model):
    """Templates d'emails personnalisables par organization"""
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='email_templates',
        verbose_name=_('organisation')
    )

    # Template identification
    template_key = models.CharField(_('clé template'), max_length=100)
    name = models.CharField(_('nom'), max_length=200)

    # Template content
    subject = models.CharField(_('sujet'), max_length=200)
    html_content = models.TextField(_('contenu HTML'))
    text_content = models.TextField(_('contenu texte'), blank=True)

    # Variables disponibles (JSON schema)
    variables = models.JSONField(_('variables'), default=list, blank=True)

    # Status
    is_active = models.BooleanField(_('actif'), default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('template email')
        verbose_name_plural = _('templates emails')
        unique_together = ['organization', 'template_key']
        ordering = ['organization', 'template_key']

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class NotificationLog(models.Model):
    """Journal des notifications envoyées"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('delivered', 'Délivré'),
        ('failed', 'Échoué'),
        ('bounced', 'Rejeté'),
    ]

    # Notification
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs',
        verbose_name=_('notification')
    )

    # Channel
    channel = models.CharField(
        _('canal'),
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push'),
            ('inapp', 'In-App'),
        ]
    )

    # Recipient
    recipient = models.CharField(_('destinataire'), max_length=200)

    # Status
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Provider data (Stripe SendGrid ID, Twilio SID, etc.)
    provider_message_id = models.CharField(_('ID message provider'), max_length=200, blank=True)

    # Error details
    error_message = models.TextField(_('message erreur'), blank=True)

    # Metadata
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)

    # Timestamps
    sent_at = models.DateTimeField(_('envoyé à'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('délivré à'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('log notification')
        verbose_name_plural = _('logs notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification']),
            models.Index(fields=['channel']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.channel} - {self.recipient} ({self.status})"
