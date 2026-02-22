import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class LinkyPoint(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='linky_point'
    )
    prm_id = models.CharField(max_length=14, unique=True, verbose_name="PRM ID")
    address = models.TextField(blank=True, verbose_name="Address")
    
    # Geolocation for Solar Analysis
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Roof details
    ROOF_ORIENTATION_CHOICES = [
        ('N', 'North'), ('NE', 'North-East'), ('E', 'East'),
        ('SE', 'South-East'), ('S', 'South'), ('SW', 'South-West'),
        ('W', 'West'), ('NW', 'North-West')
    ]
    roof_orientation = models.CharField(max_length=2, choices=ROOF_ORIENTATION_CHOICES, null=True, blank=True)
    roof_slope = models.FloatField(help_text="Slope in degrees", null=True, blank=True)

    # Subscription details (Enedis Contract)
    subscription_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Abonnement")
    subscribed_power = models.CharField(max_length=20, blank=True, null=True, verbose_name="Puissance Souscrite")
    last_index = models.FloatField(null=True, blank=True, verbose_name="Dernier Index (kWh)")

    # OAuth Tokens (WARNING: Should be encrypted in production using django-fernet-fields)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Linky {self.prm_id} ({self.user})"

class EnergyConsumption(models.Model):
    TYPE_CHOICES = [
        ('DAILY', 'Daily Consumption'),
        ('LOAD_CURVE', 'Load Curve (30min)'),
    ]
    
    linky_point = models.ForeignKey(LinkyPoint, on_delete=models.CASCADE, related_name='consumptions')
    timestamp = models.DateTimeField()
    value_kwh = models.FloatField()
    data_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='LOAD_CURVE')
    
    class Meta:
        unique_together = ('linky_point', 'timestamp', 'data_type')
        indexes = [
            models.Index(fields=['linky_point', 'timestamp']),
        ]

class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    installer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='client_requests'
    )
    client_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    unique_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.installer} for {self.client_email}"

class SolarSimulation(models.Model):
    linky_point = models.ForeignKey(LinkyPoint, on_delete=models.CASCADE, related_name='simulations')
    recommended_kwp = models.FloatField(help_text="Recommended installation size in kWp")
    estimated_savings_eur = models.FloatField(help_text="Yearly savings in EUR")
    self_consumption_rate = models.FloatField(help_text="Estimated self-consumption rate (0-1)")
    roi_years = models.FloatField(help_text="Return on investment in years")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulation for {self.linky_point} - {self.recommended_kwp}kWp"
