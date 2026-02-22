import requests
import json
from decimal import Decimal

class PVGISClient:
    """
    Client pour l'API PVGIS 5.3 (Commission Européenne).
    Documentation : https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#TMY
    """
    
    BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"
    
    def get_hourly_production(self, lat, lon, kwp=3, loss=14, angle=35, aspect=0):
        """
        Récupère la production horaire simulée sur une année type.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            kwp (float): Puissance crête installée en kWc
            loss (float): Pertes système en % (défaut 14%)
            angle (float): Inclinaison (0=horizontal, 90=vertical)
            aspect (float): Orientation (0=Sud, -90=Est, 90=Ouest)
            
        Returns:
            list: Liste de 8760 valeurs (Wh) pour chaque heure de l'année.
        """
        params = {
            'lat': lat,
            'lon': lon,
            'peakpower': kwp,
            'loss': loss,
            'angle': angle,
            'aspect': aspect,
            'outputformat': 'json',
            'startyear': 2020, # Année type récente
            'endyear': 2020,
            'pvcalculation': 1, # Activer le calcul PV
            'components': 0 # Pas besoin des composants de rayonnement détaillés
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extraction des données horaires (P = Puissance en W)
            hourly_data = []
            if 'outputs' in data and 'hourly' in data['outputs']:
                for entry in data['outputs']['hourly']:
                    # entry['P'] est la puissance en Watts pour l'heure donnée
                    hourly_data.append(entry['P'])
                    
            return hourly_data
            
        except requests.RequestException as e:
            print(f"Erreur API PVGIS : {e}")
            return []
