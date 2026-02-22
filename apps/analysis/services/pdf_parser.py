import os
import time
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class AdobePDFParser:
    """
    Service to interact with Adobe PDF Services API for extracting text and tables.
    Uses REST API directly to avoid heavy SDK dependencies.
    """
    
    BASE_URL = "https://pdf-services.adobe.io"
    AUTH_URL = "https://pdf-services.adobe.io/token"

    def __init__(self):
        self.client_id = os.environ.get("ADOBE_CLIENT_ID")
        self.client_secret = os.environ.get("ADOBE_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self):
        """Authenticates with Adobe to get a JWT access token."""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        logger.info("Authenticating with Adobe PDF Services...")
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post(self.AUTH_URL, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + (data["expires_in"] - 60) # Buffer
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Adobe: {e}")
            raise

    def _upload_file(self, file_path, media_type="application/pdf"):
        """Uploads the file to Adobe for processing."""
        token = self._get_access_token()
        
        # 1. Get Upload URI
        url = f"{self.BASE_URL}/assets"
        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key": self.client_id,
            "Content-Type": "application/json"
        }
        payload = {"mediaType": media_type}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        upload_data = response.json()
        upload_uri = upload_data["uploadUri"]
        asset_id = upload_data["assetID"]

        # 2. Upload the file binary
        with open(file_path, "rb") as f:
            upload_response = requests.put(upload_uri, data=f, headers={"Content-Type": media_type})
            upload_response.raise_for_status()
            
        return asset_id

    def extract_pdf_content(self, file_path):
        """
        Main method to extract content from a PDF.
        Returns the raw JSON structure from Adobe Extract API.
        """
        try:
            asset_id = self._upload_file(file_path)
            token = self._get_access_token()
            
            # 3. Create Extract Job
            url = f"{self.BASE_URL}/operation/extractpdf"
            headers = {
                "Authorization": f"Bearer {token}",
                "x-api-key": self.client_id,
                "Content-Type": "application/json"
            }
            payload = {
                "assetID": asset_id,
                "getCharBounds": False,
                "includeStyling": False,
                "elementsToExtract": ["text", "tables"]
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            job_location = response.headers["location"]
            
            # 4. Poll for completion
            logger.info(f"Polling for job completion: {job_location}")
            status = "IN_PROGRESS"
            while status == "IN_PROGRESS":
                time.sleep(2)
                job_response = requests.get(job_location, headers=headers)
                job_response.raise_for_status()
                job_data = job_response.json()
                status = job_data["status"]
                
                if status == "FAILED":
                    raise Exception(f"Adobe Job Failed: {job_data}")
            
            # 5. Download Result
            content_url = job_data["content"]["downloadUri"]
            result_response = requests.get(content_url)
            result_response.raise_for_status()
            
            return result_response.json() # This is the full JSON structure
            
        except Exception as e:
            logger.error(f"PDF Extraction failed: {e}")
            raise

    def parse_invoice_data(self, raw_json):
        """
        Analyzes the raw JSON to find Invoice data.
        Returns a simplified dict: {subscription_price, kwh_price, total_amount}
        """
        # This is a basic implementation. We will need to iterate on regex/logic 
        # based on real invoice examples (EDF vs Enedis vs Total).
        extracted = {
            "provider": "Unknown",
            "subscription_cost": 0.0,
            "kwh_price_hp": 0.0, # Heures Pleines
            "kwh_price_hc": 0.0, # Heures Creuses
            "total_ttc": 0.0
        }
        
        elements = raw_json.get("elements", [])
        text_lines = [el["Text"] for el in elements if "Text" in el]
        
        # Simple keyword search (To be improved with regex)
        for i, line in enumerate(text_lines):
            line_lower = line.lower()
            
            if "total à payer" in line_lower or "montant ttc" in line_lower:
                # Try to find the number in this line or next
                pass 
                
            if "abonnement" in line_lower:
                # Look for price
                pass

        return extracted

    def parse_quote_data(self, raw_json):
        """
        Analyzes raw JSON for Installer Quotes (Devis).
        """
        # Logic to find "Panneaux", "Onduleur", "Main d'oeuvre"
        items = []
        return {"items": items, "total_ht": 0, "total_ttc": 0}
