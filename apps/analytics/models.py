from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Event(models.Model):
    """Modèle pour tracker les événements business"""
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('click', 'Click'),
        ('form_submit', 'Form Submit'),
        ('signup', 'Sign Up'),
        ('login', 'Login'),
        ('purchase', 'Purchase'),
        ('subscription', 'Subscription'),
        ('custom', 'Custom'),
    ]

    # Organization context
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('organisation')
    )

    # Event data
    event_type = models.CharField(
        _('type d\'événement'),
        max_length=50,
        choices=EVENT_TYPES,
        db_index=True
    )
    event_name = models.CharField(_('nom événement'), max_length=200, db_index=True)

    # User context (optional - anonymous events possible)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name=_('utilisateur')
    )
    session_id = models.CharField(_('session ID'), max_length=200, db_index=True)

    # Event properties (JSON flexible)
    properties = models.JSONField(_('propriétés'), default=dict, blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    referrer = models.URLField(_('referrer'), blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('créé à'), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('événement')
        verbose_name_plural = _('événements')
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['organization', 'event_type']),
            models.Index(fields=['organization', 'user', '-created_at']),
            models.Index(fields=['session_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_name} ({self.event_type})"

class Metric(models.Model):
    """Métriques agrégées pour le dashboard"""
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name=_('organisation')
    )

    # Metric identification
    metric_name = models.CharField(_('nom métrique'), max_length=200)
    metric_type = models.CharField(
        _('type métrique'),
        max_length=50,
        choices=[
            ('counter', 'Counter'),
            ('gauge', 'Gauge'),
            ('histogram', 'Histogram'),
            ('summary', 'Summary'),
        ]
    )

    # Metric value
    value = models.JSONField(_('valeur'), default=dict)

    # Timestamp
    date = models.DateField(_('date'), db_index=True)
    hour = models.IntegerField(_('heure'), null=True, blank=True)

    # Metadata
    dimensions = models.JSONField(_('dimensions'), default=dict, blank=True)

    class Meta:
        verbose_name = _('métrique')
        verbose_name_plural = _('métriques')
        unique_together = ['organization', 'metric_name', 'date', 'hour']
        indexes = [
            models.Index(fields=['organization', 'date']),
            models.Index(fields=['organization', 'metric_name', '-date']),
        ]
        ordering = ['-date', '-hour']

    def __str__(self):
        return f"{self.metric_name} - {self.date}"

class DailyStats(models.Model):
    """Statistiques quotidiennes agrégées par organization"""
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name=_('organisation')
    )

    # Date
    date = models.DateField(_('date'), db_index=True)

    # Users
    new_users = models.IntegerField(_('nouveaux utilisateurs'), default=0)
    active_users = models.IntegerField(_('utilisateurs actifs'), default=0)
    returning_users = models.IntegerField(_('utilisateurs récurrents'), default=0)

    # Sessions
    total_sessions = models.IntegerField(_('sessions totales'), default=0)
    avg_session_duration = models.IntegerField(_('durée moyenne session'), default=0)

    # Page Views
    page_views = models.IntegerField(_('pages vues'), default=0)
    unique_page_views = models.IntegerField(_('pages vues uniques'), default=0)

    # Conversions
    signups = models.IntegerField(_('inscriptions'), default=0)
    purchases = models.IntegerField(_('achats'), default=0)
    subscriptions = models.IntegerField(_('abonnements'), default=0)

    # Revenue
    revenue = models.DecimalField(_('revenu'), max_digits=10, decimal_places=2, default=0)

    # Custom metrics
    custom_metrics = models.JSONField(_('métriques custom'), default=dict, blank=True)

    class Meta:
        verbose_name = _('statistiques quotidiennes')
        verbose_name_plural = _('statistiques quotidiennes')
        unique_together = ['organization', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Stats {self.organization.name} - {self.date}"

class Funnel(models.Model):
    """Tunnels de conversion"""
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='funnels',
        verbose_name=_('organisation')
    )

    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # Funnel definition (steps)
    steps = models.JSONField(_('étapes'), default=list)

    # Funnel metrics
    total_entries = models.IntegerField(_('entrées totales'), default=0)
    conversion_rate = models.DecimalField(_('taux conversion'), max_digits=5, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('tunnel')
        verbose_name_plural = _('tunnels')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Report(models.Model):
    """Rapports personnalisés"""
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('organisation')
    )

    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # Report configuration
    report_type = models.CharField(
        _('type rapport'),
        max_length=50,
        choices=[
            ('table', 'Table'),
            ('chart', 'Chart'),
            ('funnel', 'Funnel'),
            ('cohort', 'Cohort Analysis'),
        ]
    )

    # Query configuration
    metrics = models.JSONField(_('métriques'), default=list)
    dimensions = models.JSONField(_('dimensions'), default=list)
    filters = models.JSONField(_('filtres'), default=dict)

    # Scheduling
    is_scheduled = models.BooleanField(_('planifié'), default=False)
    schedule = models.CharField(_('planification'), max_length=50, blank=True)

    # Recipients
    recipients = models.JSONField(_('destinataires'), default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('rapport')
        verbose_name_plural = _('rapports')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
