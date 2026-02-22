from django.db import models
from apps.audit.models import AuditSession
from django.utils.translation import gettext_lazy as _

class DocumentAnalysis(models.Model):
    """
    Stores uploaded documents (PDFs) and their analysis results.
    Used for extracting financial data from bills or itemizing quotes.
    """
    DOCUMENT_TYPES = [
        ('INVOICE', _('Electricity Bill')),
        ('QUOTE', _('Installer Quote')),
        ('OTHER', _('Other Document')),
    ]

    STATUS_CHOICES = [
        ('PENDING', _('Analysis Pending')),
        ('PROCESSING', _('Processing with AI')),
        ('COMPLETED', _('Analysis Completed')),
        ('FAILED', _('Analysis Failed')),
    ]

    audit = models.ForeignKey(AuditSession, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='INVOICE')
    file = models.FileField(upload_to='uploads/documents/%Y/%m/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Analysis Results
    raw_json_result = models.JSONField(null=True, blank=True, help_text="Raw JSON output from Adobe PDF Services")
    extracted_data = models.JSONField(null=True, blank=True, help_text="Structured data (e.g., kwh_price, total_amount)")
    
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.status}"

class SolarSimulation(models.Model):
    audit = models.OneToOneField(AuditSession, on_delete=models.CASCADE, related_name='solar_simulation')
    
    # Paramètres de simulation
    kwp = models.FloatField(default=3.0, help_text="Puissance crête (kWc)")
    orientation = models.FloatField(default=0, help_text="0=Sud, 90=Ouest, -90=Est")
    tilt = models.FloatField(default=35, help_text="Inclinaison (degrés)")
    
    # Résultats bruts (JSON)
    hourly_production = models.JSONField(null=True, blank=True, help_text="Liste des 8760 valeurs de prod (Wh)")
    hourly_consumption = models.JSONField(null=True, blank=True, help_text="Liste des 8760 valeurs de conso (Wh) - Linky ou Estimé")
    
    # KPI calculés
    total_production_kwh = models.FloatField(default=0)
    total_consumption_kwh = models.FloatField(default=0)
    
    self_consumption_rate = models.FloatField(default=0, help_text="% Autoconsommation (0-100)")
    autarky_rate = models.FloatField(default=0, help_text="% Autarcie (0-100)")
    
    surplus_kwh = models.FloatField(default=0, help_text="Surplus injecté réseau (kWh)")
    missing_kwh = models.FloatField(default=0, help_text="Manque soutiré réseau (kWh)")
    
    # Financials
    estimated_savings_eur = models.FloatField(default=0, help_text="Economies annuelles estimées (€)")
    estimated_bill_reduction_eur = models.FloatField(default=0, help_text="% réduction facture")
    
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_kpis(self):
        """Met à jour les KPI basés sur les profils horaires"""
        if not self.hourly_production or not self.hourly_consumption:
            return
            
        prod = self.hourly_production # Liste Wh
        conso = self.hourly_consumption # Liste Wh
        
        total_prod = sum(prod)
        total_conso = sum(conso)
        
        self.total_production_kwh = total_prod / 1000
        self.total_consumption_kwh = total_conso / 1000
        
        autoconso_sum = 0
        surplus_sum = 0
        
        # Simulation heure par heure
        # On suppose que les listes sont alignées (h0 -> h8759)
        min_len = min(len(prod), len(conso))
        
        for i in range(min_len):
            p = prod[i]
            c = conso[i]
            
            autoconso = min(p, c)
            surplus = max(0, p - c)
            
            autoconso_sum += autoconso
            surplus_sum += surplus
            
        # Calcul KPI
        if total_prod > 0:
            self.self_consumption_rate = (autoconso_sum / total_prod) * 100
        else:
            self.self_consumption_rate = 0
            
        if total_conso > 0:
            self.autarky_rate = (autoconso_sum / total_conso) * 100
        else:
            self.autarky_rate = 0
            
        self.surplus_kwh = surplus_sum / 1000
        self.missing_kwh = (total_conso - autoconso_sum) / 1000
        
        # Financial estimation (Default 0.22€/kWh if no bill analyzed)
        kwh_price = 0.22 
        # Check if an invoice was analyzed in the same audit
        invoice = DocumentAnalysis.objects.filter(audit=self.audit, document_type='INVOICE', status='COMPLETED').first()
        if invoice and invoice.extracted_data and invoice.extracted_data.get('kwh_price'):
            kwh_price = float(invoice.extracted_data.get('kwh_price'))
            
        self.estimated_savings_eur = (autoconso_sum / 1000) * kwh_price
        if total_conso > 0:
            self.estimated_bill_reduction_eur = (self.estimated_savings_eur / ((total_conso / 1000) * kwh_price)) * 100
            
        self.save()

    def run_pvgis_simulation(self, lat, lon):
        from apps.scrapers.services.pvgis import PVGISClient
        client = PVGISClient()
        
        # Appel API
        production_data = client.get_hourly_production(
            lat=lat,
            lon=lon,
            kwp=self.kwp,
            angle=self.tilt,
            aspect=self.orientation
        )
        
        if production_data:
            self.hourly_production = production_data
            self.save()
            # Si on a déjà la conso, on lance le calcul
            if self.hourly_consumption:
                 self.calculate_kpis()
            return True
        return False

    def __str__(self):
        return f"Simulateur {self.kwp}kWc - Audit #{self.audit.id}"
