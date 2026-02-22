import os
import django
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.energy.services.enedis_client import EnedisClient, SANDBOX_PRMS
from apps.energy.models import LinkyPoint, EnergyConsumption
from django.contrib.auth import get_user_model

User = get_user_model()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_history():
    # 1. Setup environnement
    user = User.objects.first() # On prend le premier utilisateur pour le test
    if not user:
        logger.error("Aucun utilisateur trouvé en base.")
        return

    client = EnedisClient()
    prm = SANDBOX_PRMS['active_charge'] # Client 1 - Le plus riche en données
    
    # Check if PRM already exists (maybe for another user)
    linky = LinkyPoint.objects.filter(prm_id=prm).first()
    if linky:
        linky.user = user
        linky.save()
    else:
        linky = LinkyPoint.objects.create(
            user=user,
            prm_id=prm,
            address='123 Avenue du Bac à Sable, 75000 Paris'
        )

    # 2. Authentification
    try:
        token_data = client.get_token()
        access_token = token_data.get('access_token')
    except Exception as e:
        logger.error(f"Erreur Auth : {e}")
        return

    # 3. Boucle sur 3 ans (From 2023 up to Yesterday)
    # System time is 2026-02-07, so we stop at 2026-02-06 to avoid "future" data errors
    start_global = datetime(2023, 1, 1)
    end_global = datetime.now() - timedelta(days=1)
    
    current_start = start_global
    
    while current_start < end_global:
        current_end = current_start + relativedelta(months=3)
        if current_end > end_global:
            current_end = end_global
            
        logger.info(f"Importation du {current_start.date()} au {current_end.date()}...")
        
        try:
            # Récupération journalière (DAILY)
            data = client.fetch_daily_consumption(access_token, prm, current_start, current_end)
            readings = data.get('meter_reading', {}).get('interval_reading', [])
            
            objs = []
            for r in readings:
                ts = datetime.fromisoformat(r['date'])
                val = float(r['value']) / 1000.0 # Convert Wh to kWh
                
                objs.append(EnergyConsumption(
                    linky_point=linky,
                    timestamp=ts,
                    value_kwh=val,
                    data_type='DAILY'
                ))
            
            # Sauvegarde en masse (ignore les doublons)
            EnergyConsumption.objects.bulk_create(objs, ignore_conflicts=True)
            logger.info(f"  -> {len(objs)} points de consommation importés.")
            
        except Exception as e:
            logger.warning(f"  -> Erreur sur cette période : {e}")
        
        current_start = current_end

    logger.info("IMPORTATION TERMINÉE.")

if __name__ == "__main__":
    import_history()
