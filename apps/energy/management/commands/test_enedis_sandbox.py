from django.core.management.base import BaseCommand
from apps.energy.services.enedis_client import EnedisClient, SANDBOX_PRMS
from django.utils import timezone
from datetime import timedelta
import json

class Command(BaseCommand):
    help = 'Test connection to Enedis Sandbox API'

    def handle(self, *args, **options):
        self.stdout.write("🔌 Testing Enedis Sandbox Connection...")
        
        client = EnedisClient()
        
        if not client.is_sandbox:
            self.stdout.write(self.style.ERROR("❌ EnedisClient is NOT in Sandbox mode! Check URLs."))
            return

        # 1. AUTHENTICATION
        try:
            self.stdout.write("🔑 Requesting Access Token (Client Credentials)...")
            token_response = client.get_token()
            access_token = token_response.get("access_token")
            
            if access_token:
                self.stdout.write(self.style.SUCCESS(f"✅ Token Received: {access_token[:10]}..."))
            else:
                self.stdout.write(self.style.ERROR(f"❌ No token in response: {token_response}"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Auth Failed: {str(e)}"))
            return

        # 2. FETCH DATA (Load Curve)
        prm_id = SANDBOX_PRMS['active_charge'] # 11453290002823
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7) # Last 7 days
        
        self.stdout.write(f"📉 Fetching Load Curve for PRM {prm_id} ({start_date} to {end_date})...")
        
        try:
            data = client.fetch_load_curve(access_token, prm_id, start_date, end_date)
            
            # Check for Enedis API Error structure
            if "error" in data:
                 self.stdout.write(self.style.ERROR(f"❌ API Error: {data}"))
            elif "meter_reading" in data:
                reading = data['meter_reading']
                points = reading.get('interval_reading', [])
                self.stdout.write(self.style.SUCCESS(f"✅ Data Received! {len(points)} data points found."))
                # Print first point sample
                if points:
                    self.stdout.write(f"   Sample: {points[0]}")
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Unexpected Response Structure: {data.keys()}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Data Fetch Failed: {str(e)}"))

