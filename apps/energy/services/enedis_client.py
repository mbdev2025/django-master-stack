import os
import requests
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# Liste des PRM fictifs officiels Enedis pour le Bac à sable
SANDBOX_PRMS = {
    'standard': '22516914714270',    # Consommation standard avec courbe
    'active_charge': '11453290002823', # Courbe de charge active
    'no_load_curve': '32320647321714', # Pas de courbe de charge
    'production': '24880057139941',    # Production seule
    'mixed': '12345678901234',         # Mixte (Conso + Prod)
    'autoconsommation': '12655648759651',
}

class EnedisClient:
    def __init__(self):
        # Configuration is loaded from settings to allow dynamic environment switching (Sandbox/Prod)
        self.base_url = getattr(settings, 'ENEDIS_API_BASE_URL', "https://gw.enedis.fr/v1")
        self.auth_url = getattr(settings, 'ENEDIS_AUTH_URL', "https://mon-compte-particulier.enedis.fr/dataconnect/v1/oauth2/authorize")
        self.token_url = getattr(settings, 'ENEDIS_TOKEN_URL', "https://gw.enedis.fr/v1/oauth2/token")
        
        self.client_id = os.environ.get("ENEDIS_CLIENT_ID")
        self.client_secret = os.environ.get("ENEDIS_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("ENEDIS_REDIRECT_URI", getattr(settings, 'ENEDIS_REDIRECT_URI', ''))
        
        # Détection automatique du mode Sandbox via l'URL
        self.is_sandbox = "sandbox" in self.token_url.lower()
        if self.is_sandbox:
            logger.info("EnedisClient operating in SANDBOX mode.")

        # mTLS Certificate Support (Optional)
        cert_file = getattr(settings, 'ENEDIS_CERT_FILE', os.environ.get("ENEDIS_CERT_FILE"))
        key_file = getattr(settings, 'ENEDIS_KEY_FILE', os.environ.get("ENEDIS_KEY_FILE"))
        if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
            self.cert = (cert_file, key_file)
            logger.info(f"EnedisClient initialized with mTLS certificates: {cert_file}")
        else:
            self.cert = None
            if cert_file or key_file:
                logger.warning("Enedis certificate files configured but not found.")

    def get_authorization_url(self, state=None):
        """Generates the Enedis OAuth2 authorization URL."""
        if self.is_sandbox:
            logger.warning("Authorization URL is NOT needed in Sandbox mode. Use client_credentials flow.")
            
        # Scope list for v5: permits access to consumption, identity and contractual data
        # Note: Scopes must be space-separated and authorized in Enedis portal
        scopes = "openid identity contact contracts addresses daily_consumption consumption_load_curve"
        
        url = (
            f"{self.auth_url}?"
            f"client_id={self.client_id}&"
            f"duration=P3D&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={scopes}"
        )
        if state:
            url += f"&state={state}"
        logger.info(f"Generated Authorization URL: {url}")
        return url


    def get_token(self, code=None):
        """
        Generic token retrieval. 
        In Sandbox, uses client_credentials (no code needed).
        In Production, uses authorization_code (requires code).
        """
        if self.is_sandbox:
            logger.info("Requesting SANDBOX token via client_credentials.")
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        else:
            if not code:
                raise ValueError("Authorization code is required for production token exchange.")
            logger.info("Requesting PRODUCTION token via authorization_code.")
            payload = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
            }
        
        return self._request('POST', self.token_url, data=payload)

    def _request(self, method, url, **kwargs):
        """Helper to make requests with error logging and optional mTLS."""
        # Add default headers to avoid WAF blocking
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        kwargs['headers'] = headers

        if self.cert:
            kwargs['cert'] = self.cert
        
        try:
            logger.debug(f"Calling Enedis API [{method}] {url}")
            response = requests.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                logger.error(f"Enedis API Error {response.status_code}: {response.text}")
                # Try to log JSON detail if possible
                try:
                    error_detail = response.json()
                    logger.error(f"Enedis API Error Details: {error_detail}")
                except:
                    pass
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.exception(f"HTTP Error calling Enedis API: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error calling Enedis API: {e}")
            raise

    # Original methods kept for compatibility but pointed to the new generic get_token
    def exchange_code(self, code):
        return self.get_token(code=code)

    def refresh_token(self, refresh_token):
        """Refreshes the access token using the refresh token."""
        logger.info("Refreshing access token.")
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return self._request('POST', self.token_url, data=payload)

    def fetch_load_curve(self, access_token, prm_id, start_date, end_date):
        """Fetches the load curve (courbe de charge) from Enedis."""
        headers = {
            "Authorization": f"Bearer {access_token}", 
            "Accept": "application/json",
            "x-api-key": self.client_id
        }
        params = {
            "usage_point_id": prm_id,
            "start": start_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
        }
        # Based on JWT context discovery
        version = "v5" if self.is_sandbox else "v4"
        if self.is_sandbox:
            endpoint = f"{self.base_url}/metering_data_clc/{version}/consumption_load_curve"
        else:
            endpoint = f"{self.base_url}/{version}/metering/consumption_load_curve"
        return self._request('GET', endpoint, headers=headers, params=params)

    def fetch_daily_consumption(self, access_token, prm_id, start_date, end_date):
        """Fetches daily consumption."""
        headers = {
            "Authorization": f"Bearer {access_token}", 
            "Accept": "application/json",
            "x-api-key": self.client_id
        }
        params = {
            "usage_point_id": prm_id,
            "start": start_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
        }
        version = "v5" if self.is_sandbox else "v4"
        if self.is_sandbox:
            endpoint = f"{self.base_url}/metering_data_dc/{version}/daily_consumption"
        else:
            endpoint = f"{self.base_url}/{version}/metering/daily_consumption"
        return self._request('GET', endpoint, headers=headers, params=params)
