"""Weather API integration for environmental data"""

import requests
from typing import Optional
from ..models.workout import EnvironmentalData


class WeatherAPI:
    """
    Interface for fetching weather/environmental data.
    Supports OpenWeatherMap API (requires API key).
    Can be extended for other weather services.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather API
        
        Args:
            api_key: API key for OpenWeatherMap (optional, can use mock data)
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_current_conditions(
        self,
        location: str,
        units: str = "imperial"
    ) -> Optional[EnvironmentalData]:
        """
        Get current weather conditions for a location
        
        Args:
            location: City name or coordinates (e.g., "New York,NY" or "40.7128,-74.0060")
            units: "imperial" for Fahrenheit, "metric" for Celsius
            
        Returns:
            EnvironmentalData or None if API unavailable
        """
        if not self.api_key:
            # Return mock data for development/testing
            return self._get_mock_conditions(location)
        
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': units
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return EnvironmentalData(
                temperature_fahrenheit=data['main']['temp'],
                humidity_percent=data['main']['humidity'],
                location=location,
                wind_speed_mph=data.get('wind', {}).get('speed', 0.0)
            )
        
        except Exception as e:
            # Fallback to mock data on error
            print(f"Weather API error: {e}. Using mock data.")
            return self._get_mock_conditions(location)
    
    def _get_mock_conditions(self, location: str) -> EnvironmentalData:
        """Generate mock environmental data for testing"""
        # Simple mock based on location name
        # In production, this could use cached data or default values
        import random
        
        # Simulate different conditions
        base_temp = 70.0
        if 'indoor' in location.lower() or 'gym' in location.lower():
            base_temp = 68.0
        
        return EnvironmentalData(
            temperature_fahrenheit=base_temp + random.uniform(-5, 10),
            humidity_percent=random.uniform(30, 70),
            location=location,
            wind_speed_mph=random.uniform(0, 10)
        )

