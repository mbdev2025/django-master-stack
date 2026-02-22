import os
import django
import logging
from datetime import datetime, timedelta

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Configuration des logs APRES django.setup()
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

from apps.energy.services.enedis_client import EnedisClient, SANDBOX_PRMS

def run_test():
    client = EnedisClient()
    
    # 1. Obtenir le token Sandbox
    logger.info("--- TEST 1: OBTENTION DU TOKEN SANDBOX ---")
    try:
        token_data = client.get_token()
        access_token = token_data.get('access_token')
        logger.info(f"SUCCESS: Token obtenu ! Response: {token_data}")
    except Exception as e:
        logger.error(f"FAILED: Impossible d'obtenir le token : {e}")
        return

    # 2. Récupérer des données pour le PRM standard
    prm = SANDBOX_PRMS['active_charge']
    # Test avec une période HISTORIQUE (2019 est l'année préférée de la sandbox Enedis)
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 1, 7)
    
    logger.info(f"--- TEST 2: RÉCUPÉRATION DONNÉES PRM {prm} ---")
    
    # Affichage de la commande CURL pour test manuel
    curl_cmd = f"curl -v -X GET 'https://ext.prod-sandbox.api.enedis.fr/v5/metering/daily_consumption/?usage_point_id={prm}&start=2019-01-01&end=2019-01-07' -H 'Authorization: Bearer {access_token}' -H 'x-api-key: {client.client_id}'"
    print(f"\nCOMMANDE CURL A TESTER :\n{curl_cmd}\n")

    try:
        data = client.fetch_daily_consumption(access_token, prm, start_date, end_date)
        logger.info(f"SUCCESS: Données récupérées !")
    except Exception as e:
        logger.error(f"FAILED: Erreur : {e}")

if __name__ == "__main__":
    run_test()
