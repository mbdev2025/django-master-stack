import requests
from datetime import datetime

class WeatherClient:
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def fetch_solar_data(self, latitude, longitude, start_date, end_date):
        """
        Fetches historical weather data (irradiance, temperature) from Open-Meteo.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,shortwave_radiation",
            "timezone": "auto"
        }
        
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
