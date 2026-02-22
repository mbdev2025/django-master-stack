import requests

def get_lat_lon_from_address(address):
    """
    Geocode une adresse via l'API Adresse Data.gouv.fr (BAN).
    
    Args:
        address (str): Adresse complète (ex: '8 avenue foch paris 75016')
        
    Returns:
        tuple (float, float) ou (None, None): (lat, lon)
    """
    if not address:
        return None, None
        
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {'q': address, 'limit': 1}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'features' in data and len(data['features']) > 0:
            coords = data['features'][0]['geometry']['coordinates']
            # API Gouv returns [lon, lat]
            return coords[1], coords[0]
            
    except requests.RequestException as e:
        print(f"Erreur Geocoding : {e}")
        
    return None, None
