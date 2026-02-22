
import os
import django
import random
from datetime import datetime, timedelta
import logging

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.energy.models import LinkyPoint, EnergyConsumption
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inject_data():
    logger.info("Injecting demo data...")
    
    # 1. Get Jean Dupont
    user = User.objects.filter(email='jean.dupont@example.com').first()
    if not user:
        logger.error("User Jean Dupont not found. Please login as demo first.")
        return

    # 2. Get Linky Point
    linky = LinkyPoint.objects.filter(user=user).first()
    if not linky:
        logger.error("Linky Point not found for Jean Dupont.")
        return
        
    logger.info(f"Target Linky: {linky.prm_id}")

    # 3. Clear existing conflicting data (optional, but good for clean slate)
    # EnergyConsumption.objects.filter(linky_point=linky).delete()

    # 4. Generate Data
    # Reference Date: 2026-02-07 (Today)
    # We want data up to Yesterday (2026-02-06)
    
    base_date = datetime(2026, 2, 7)
    objs = []
    
    # Generate 3 years of history (approx 1100 days)
    for i in range(1, 1100):
        date = base_date - timedelta(days=i)
        
        # Random consumption between 5 and 20 kWh
        # Higher in winter (Jan/Feb/Dec)
        val = random.uniform(5.0, 15.0)
        if date.month in [1, 2, 12]:
            val += random.uniform(5.0, 10.0)
            
        objs.append(EnergyConsumption(
            linky_point=linky,
            timestamp=date,
            value_kwh=round(val, 2),
            data_type='DAILY'
        ))

    # Bulk Create
    EnergyConsumption.objects.bulk_create(objs, ignore_conflicts=True)
    logger.info(f"Injected {len(objs)} records ending on {base_date - timedelta(days=1)}")

if __name__ == "__main__":
    inject_data()
