from django.db import models
from django.conf import settings

class AuditSession(models.Model):
    """Un dossier d'audit pour un client"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, default="Audit Résidentiel")
    
    # Facturation & Technique
    subscription_price = models.DecimalField(max_digits=6, decimal_places=2, default=15.00, help_text="Abonnement mensuel €")
    kwh_price_hc = models.DecimalField(max_digits=6, decimal_places=4, default=0.2068, help_text="Prix kWh HC")
    
    # Localisation
    address = models.CharField(max_length=255, blank=True, null=True, help_text="Adresse complète")
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial Projections
    yearly_savings_estimated = models.DecimalField(max_digits=10, decimal_places=2, default=1200.00, help_text="Economie annuelle estimée (€)")
    electricity_inflation = models.DecimalField(max_digits=4, decimal_places=2, default=5.0, help_text="Inflation élec % / an")

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class ApplianceCategory(models.TextChoices):
    KITCHEN = 'kitchen', 'Cuisine'
    LIVING = 'living', 'Salon / Multimédia'
    HEATING = 'heating', 'Chauffage / Clim'
    WATER = 'water', 'Eau Chaude / Sanitaire'
    OUTDOOR = 'outdoor', 'Extérieur / Piscine'
    OTHER = 'other', 'Autre'

class Equipment(models.Model):
    """Un équipement recensé chez le client"""
    audit = models.ForeignKey(AuditSession, on_delete=models.CASCADE, related_name='equipments')
    name = models.CharField(max_length=100) # ex: "Frigo Américain"
    category = models.CharField(max_length=20, choices=ApplianceCategory.choices, default=ApplianceCategory.KITCHEN)
    
    power_watts = models.IntegerField(help_text="Puissance en Watts")
    qty = models.IntegerField(default=1)
    
    # Usage Profile
    hours_per_day_winter = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    hours_per_day_summer = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    
    # Is it runnable at night? (Shiftable)
    is_shiftable = models.BooleanField(default=False, help_text="Peut être piloté/décalé ?")

    def yearly_consumption(self):
        # Approx simple : 6 mois hiver / 6 mois été
        daily_w = (self.hours_per_day_winter * self.power_watts) + (self.hours_per_day_summer * self.power_watts)
        # Moyenne journalière * 365 * Qté
        avg_daily_kwh = (daily_w / 2) / 1000
        return round(avg_daily_kwh * 365 * self.qty)

    def __str__(self):
        return f"{self.qty}x {self.name} ({self.power_watts}W)"

class CostCategory(models.TextChoices):
    PANELS = 'panels', 'Panneaux Photovoltaïques'
    INVERTER = 'inverter', 'Onduleurs / Micro-onduleurs'
    STRUCTURE = 'structure', 'Système d\'intégration / Rails'
    ELEC = 'elec', 'Coffrets / Câblage'
    ADMIN = 'admin', 'Administratif (Consuel, Mairie, Etudes)'
    LOGISTIC = 'logistic', 'Location Engin / Logistique'
    LABOR = 'labor', 'Main d\'œuvre / Pose'
    BATTERY = 'battery', 'Stockage / Batteries'
    OTHER = 'other', 'Autre'

class ProjectQuote(models.Model):
    """Le chiffrage du projet"""
    audit = models.OneToOneField(AuditSession, on_delete=models.CASCADE, related_name='quote')
    updated_at = models.DateTimeField(auto_now=True)
    
    # PDF Import
    source_file = models.FileField(upload_to='quotes/', null=True, blank=True)
    
    def total_ht(self):
        return sum(item.total_price() for item in self.items.all())
    
    def total_ttc(self):
        # TVA simplifiée 20% pour l'instant (à affiner selon règles 10% / 20%)
        return self.total_ht() * 1.20

class QuoteLineItem(models.Model):
    quote = models.ForeignKey(ProjectQuote, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=20, choices=CostCategory.choices, default=CostCategory.OTHER)
    description = models.CharField(max_length=255) # ex: "12x Panneaux DualSun 500W"
    
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    unit_price_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def total_price(self):
        return float(self.quantity) * float(self.unit_price_ht)
