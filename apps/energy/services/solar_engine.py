from datetime import timedelta
from .weather_client import WeatherClient

class SolarSimulator:
    def __init__(self, linky_point):
        self.linky_point = linky_point
        self.weather_client = WeatherClient()

    def simulate(self, kwp_size=3.0, efficiency=0.85):
        """
        Runs a simulation for a specific installation size (kWp).
        
        Logic (Simplified MVP):
        1. Fetch historical weather data for the location.
        2. Calculate potential production per hour (Irradiance * Area * Efficiency).
        3. Compare with actual consumption (Load Curve) hour by hour.
        4. Calculate Self-Consumption (Production used directly) vs Surplus (Exported).
        5. Estimate savings based on grid price vs feed-in tariff.
        """
        
        # 1. Validation
        if not self.linky_point.latitude or not self.linky_point.longitude:
            raise ValueError("LinkyPoint must have latitude and longitude.")
            
        # Placeholder for complex logic
        # In a real implementation, we would:
        # - Query database for EnergyConsumption (Load Curve)
        # - Query Weather API
        # - Iterate timestamp by timestamp
        
        return {
            "recommended_kwp": kwp_size,
            "estimated_production_kwh": 4200.0, # Dummy
            "self_consumption_rate": 0.65,      # Dummy
            "estimated_savings_eur": 850.0,     # Dummy
            "roi_years": 7.5                    # Dummy
        }
