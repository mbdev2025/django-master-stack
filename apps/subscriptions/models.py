from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Plan(models.Model):
    """Plans d'abonnement disponibles"""
    BILLING_CYCLES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]

    # Identité
    name = models.CharField(_('nom'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True, max_length=100)
    description = models.TextField(_('description'), blank=True)

    # Pricing
    price = models.DecimalField(_('prix'), max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(_('cycle facturation'), max_length=20, choices=BILLING_CYCLES)
    currency = models.CharField(_('devise'), max_length=3, default='EUR')

    # Features
    features = models.JSONField(_('fonctionnalités'), default=list, blank=True)
    max_users = models.IntegerField(_('utilisateurs max'), null=True, blank=True)
    max_storage_gb = models.IntegerField(_('stockage max GB'), null=True, blank=True)
    api_calls_per_month = models.IntegerField(_('appels API/mois'), null=True, blank=True)

    # Trial
    trial_days = models.IntegerField(_('jours essai'), default=0)
    trial_requires_card = models.BooleanField(_('carte requise pour essai'), default=False)

    # Limits & Quotas
    quotas = models.JSONField(_('quotas'), default=dict, blank=True)

    # Display
    is_active = models.BooleanField(_('actif'), default=True)
    is_popular = models.BooleanField(_('populaire'), default=False)
    display_order = models.IntegerField(_('ordre affichage'), default=0)

    # Stripe Integration
    stripe_price_id = models.CharField(_('Stripe Price ID'), max_length=200, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')
        ordering = ['display_order', 'price']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency}/{self.get_billing_cycle_display()})"

class Subscription(models.Model):
    """Abonnements utilisateurs/organizations"""
    STATUS_CHOICES = [
        ('trialing', 'En essai'),
        ('active', 'Actif'),
        ('past_due', 'En retard'),
        ('canceled', 'Annulé'),
        ('unpaid', 'Impayé'),
        ('incomplete', 'Incomplet'),
    ]

    # Organization/User
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('organisation')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('utilisateur')
    )

    # Plan
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('plan')
    )

    # Status
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='trialing')

    # Dates
    trial_end = models.DateTimeField(_('fin essai'), null=True, blank=True)
    current_period_start = models.DateTimeField(_('début période courante'))
    current_period_end = models.DateTimeField(_('fin période courante'))
    cancel_at_period_end = models.BooleanField(_('annuler fin période'), default=False)

    # Pricing
    amount = models.DecimalField(_('montant'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('devise'), max_length=3, default='EUR')

    # Stripe Integration
    stripe_subscription_id = models.CharField(_('Stripe Subscription ID'), max_length=200, blank=True)
    stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=200, blank=True)

    # Usage tracking
    current_usage = models.JSONField(_('usage actuel'), default=dict, blank=True)
    usage_reset_date = models.DateField(_('date reset usage'), null=True, blank=True)

    # Metadata
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('abonnement')
        verbose_name_plural = _('abonnements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_subscription_id']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name}"

    @property
    def is_active(self):
        return self.status in ['active', 'trialing']

    @property
    def days_until_renewal(self):
        from datetime import timezone
        if self.current_period_end:
            return (self.current_period_end - timezone.now()).days
        return None

class Invoice(models.Model):
    """Factures pour les abonnements"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('open', 'Ouverte'),
        ('paid', 'Payée'),
        ('void', 'Annulée'),
        ('uncollectible', 'Recouvrable'),
    ]

    # Organization
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('organisation')
    )

    # Subscription
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices',
        verbose_name=_('abonnement')
    )

    # User
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices',
        verbose_name=_('utilisateur')
    )

    # Invoice Details
    invoice_number = models.CharField(_('numéro facture'), max_length=200, unique=True)
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Amounts
    subtotal = models.DecimalField(_('sous-total'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('montant taxe'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('devise'), max_length=3, default='EUR')

    # Dates
    period_start = models.DateField(_('début période'))
    period_end = models.DateField(_('fin période'))
    due_date = models.DateField(_('date échéance'))

    # Payment
    paid_at = models.DateTimeField(_('payée à'), null=True, blank=True)
    payment_method = models.CharField(_('moyen paiement'), max_length=50, blank=True)

    # Stripe Integration
    stripe_invoice_id = models.CharField(_('Stripe Invoice ID'), max_length=200, blank=True)

    # PDF
    invoice_pdf = models.FileField(_('PDF facture'), upload_to='invoices/%Y/%m/', blank=True)

    # Metadata
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('facture')
        verbose_name_plural = _('factures')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_invoice_id']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.total} {self.currency}"

class PaymentMethod(models.Model):
    """Moyens de paiement des utilisateurs"""
    PAYMENT_TYPES = [
        ('card', 'Carte bancaire'),
        ('sepa_debit', 'Prélèvement SEPA'),
        ('paypal', 'PayPal'),
    ]

    # User
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name=_('utilisateur')
    )

    # Payment Details
    payment_type = models.CharField(_('type paiement'), max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(_('défaut'), default=False)

    # Card Details (encrypted in Stripe)
    card_last4 = models.CharField(_('carte derniers chiffres'), max_length=4, blank=True)
    card_brand = models.CharField(_('carte marque'), max_length=20, blank=True)
    card_exp_month = models.IntegerField(_('carte expiration mois'), null=True, blank=True)
    card_exp_year = models.IntegerField(_('carte expiration année'), null=True, blank=True)

    # Stripe Integration
    stripe_payment_method_id = models.CharField(_('Stripe Payment Method ID'), max_length=200, blank=True)

    # Metadata
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('moyen paiement')
        verbose_name_plural = _('moyens paiement')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.card_last4}"

class UsageRecord(models.Model):
    """Enregistrements d'utilisation pour pricing basé sur l'usage"""
    # Subscription
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name=_('abonnement')
    )

    # Usage Details
    metric_name = models.CharField(_('nom métrique'), max_length=100)
    quantity = models.IntegerField(_('quantité'), default=1)
    unit_price = models.DecimalField(_('prix unitaire'), max_digits=10, decimal_places=2, default=0)

    # Amount
    amount = models.DecimalField(_('montant'), max_digits=10, decimal_places=2)

    # Description
    description = models.TextField(_('description'), blank=True)

    # Timestamp
    recorded_at = models.DateTimeField(_('enregistré à'), auto_now_add=True)

    class Meta:
        verbose_name = _("enregistrement usage")
        verbose_name_plural = _("enregistrements usage")
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['subscription', '-recorded_at']),
            models.Index(fields=['metric_name']),
        ]

    def __str__(self):
        return f"{self.metric_name} - {self.quantity} x {self.unit_price}"
