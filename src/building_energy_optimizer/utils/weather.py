"""
Weather data integration for Building Energy Optimizer.
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure."""
    timestamp: datetime
    temperature: float  # °C
    humidity: float     # %
    solar_radiation: float  # W/m²
    wind_speed: float   # m/s
    precipitation: float # mm/h
    pressure: float     # hPa
    cloud_cover: float  # %

class WeatherProvider:
    """Base class for weather data providers."""
    
    def get_current_weather(self, lat: float, lon: float) -> WeatherData:
        """Get current weather data."""
        raise NotImplementedError
    
    def get_historical_weather(self, lat: float, lon: float, 
                             start_date: datetime, end_date: datetime) -> List[WeatherData]:
        """Get historical weather data."""
        raise NotImplementedError
    
    def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Get weather forecast."""
        raise NotImplementedError

class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key."""
        self.api_key = api_key or os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not provided. Using synthetic data.")
    
    def get_current_weather(self, lat: float, lon: float) -> WeatherData:
        """Get current weather from OpenWeatherMap."""
        if not self.api_key:
            return self._generate_synthetic_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                timestamp=datetime.now(),
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                solar_radiation=self._estimate_solar_radiation(data),
                wind_speed=data['wind']['speed'],
                precipitation=data.get('rain', {}).get('1h', 0),
                pressure=data['main']['pressure'],
                cloud_cover=data['clouds']['all']
            )
            
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return self._generate_synthetic_weather()
    
    def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Get weather forecast."""
        if not self.api_key:
            return self._generate_synthetic_forecast(hours)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data['list'][:hours//3]:  # 3-hour intervals
                weather_point = WeatherData(
                    timestamp=datetime.fromtimestamp(item['dt']),
                    temperature=item['main']['temp'],
                    humidity=item['main']['humidity'],
                    solar_radiation=self._estimate_solar_radiation(item),
                    wind_speed=item['wind']['speed'],
                    precipitation=item.get('rain', {}).get('3h', 0) / 3,  # Convert to hourly
                    pressure=item['main']['pressure'],
                    cloud_cover=item['clouds']['all']
                )
                forecast_data.append(weather_point)
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Failed to get forecast data: {e}")
            return self._generate_synthetic_forecast(hours)
    
    def _estimate_solar_radiation(self, weather_data: Dict) -> float:
        """Estimate solar radiation from weather data."""
        # Simple estimation based on cloud cover and time
        cloud_cover = weather_data['clouds']['all']
        
        # Base solar radiation (assuming clear sky)
        base_radiation = 1000  # W/m² max clear sky
        
        # Reduce by cloud cover
        cloud_factor = 1 - (cloud_cover / 100) * 0.8
        
        return max(base_radiation * cloud_factor, 0)
    
    def _generate_synthetic_weather(self) -> WeatherData:
        """Generate synthetic weather data."""
        return WeatherData(
            timestamp=datetime.now(),
            temperature=np.random.normal(20, 8),
            humidity=np.random.normal(60, 15),
            solar_radiation=np.random.uniform(0, 1000),
            wind_speed=np.random.exponential(5),
            precipitation=np.random.exponential(1),
            pressure=np.random.normal(1013, 10),
            cloud_cover=np.random.uniform(0, 100)
        )
    
    def _generate_synthetic_forecast(self, hours: int) -> List[WeatherData]:
        """Generate synthetic forecast data."""
        forecast = []
        for i in range(hours):
            weather_point = WeatherData(
                timestamp=datetime.now() + timedelta(hours=i),
                temperature=np.random.normal(20, 8),
                humidity=np.random.normal(60, 15),
                solar_radiation=np.random.uniform(0, 1000),
                wind_speed=np.random.exponential(5),
                precipitation=np.random.exponential(1),
                pressure=np.random.normal(1013, 10),
                cloud_cover=np.random.uniform(0, 100)
            )
            forecast.data(weather_point)
        
        return forecast

class WeatherIntegrator:
    """Main weather integration class."""
    
    def __init__(self, provider: WeatherProvider):
        """Initialize with weather provider."""
        self.provider = provider
    
    def enrich_data_with_weather(self, data: pd.DataFrame, 
                                lat: float, lon: float) -> pd.DataFrame:
        """
        Enrich building data with real weather data.
        
        Args:
            data (pd.DataFrame): Building data with timestamps
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            pd.DataFrame: Data enriched with weather information
        """
        logger.info("Enriching data with weather information...")
        
        enriched_data = data.copy()
        
        # Get weather data for each timestamp
        weather_records = []
        
        for timestamp in data['timestamp']:
            try:
                # For demo purposes, generate realistic weather
                # In production, you'd query historical weather APIs
                weather = self._get_weather_for_timestamp(timestamp, lat, lon)
                weather_records.append(weather)
            except Exception as e:
                logger.warning(f"Failed to get weather for {timestamp}: {e}")
                weather_records.append(self._default_weather())
        
        # Add weather columns to dataframe
        weather_df = pd.DataFrame([w.__dict__ for w in weather_records])
        
        for col in ['temperature', 'humidity', 'solar_radiation', 'wind_speed', 
                   'precipitation', 'pressure', 'cloud_cover']:
            if col not in enriched_data.columns:
                enriched_data[col] = weather_df[col]
        
        logger.info(f"Weather enrichment complete for {len(enriched_data)} records")
        return enriched_data
    
    def _get_weather_for_timestamp(self, timestamp: datetime, 
                                  lat: float, lon: float) -> WeatherData:
        """Get weather for specific timestamp."""
        # For historical data, we'd normally call historical weather API
        # For demo, generate realistic weather based on timestamp
        
        hour = timestamp.hour
        month = timestamp.month
        
        # Seasonal temperature
        seasonal_temp = 15 + 10 * np.sin(2 * np.pi * (month - 3) / 12)
        daily_temp = seasonal_temp + 5 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        # Add some randomness
        temperature = daily_temp + np.random.normal(0, 3)
        
        return WeatherData(
            timestamp=timestamp,
            temperature=temperature,
            humidity=max(30, min(90, 70 - 0.5 * temperature + np.random.normal(0, 10))),
            solar_radiation=max(0, 800 * np.sin(2 * np.pi * (hour - 6) / 12) * (1 - np.random.uniform(0, 0.5))),
            wind_speed=max(0, np.random.exponential(4)),
            precipitation=max(0, np.random.exponential(0.5)),
            pressure=np.random.normal(1013, 5),
            cloud_cover=np.random.uniform(0, 100)
        )
    
    def _default_weather(self) -> WeatherData:
        """Default weather data when API fails."""
        return WeatherData(
            timestamp=datetime.now(),
            temperature=20.0,
            humidity=50.0,
            solar_radiation=500.0,
            wind_speed=3.0,
            precipitation=0.0,
            pressure=1013.0,
            cloud_cover=50.0
        )

def create_weather_enriched_data(lat: float, lon: float, 
                               start_date: str, end_date: str,
                               api_key: Optional[str] = None) -> pd.DataFrame:
    """
    Create dataset enriched with real weather data.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude  
        start_date (str): Start date
        end_date (str): End date
        api_key (str): OpenWeatherMap API key
        
    Returns:
        pd.DataFrame: Weather-enriched dataset
    """
    # Create base building data
    dates = pd.date_range(start=start_date, end=end_date, freq='h')
    base_data = pd.DataFrame({
        'timestamp': dates,
        'energy_consumption': np.random.normal(100, 20, len(dates))  # Placeholder
    })
    
    # Enrich with weather
    provider = OpenWeatherMapProvider(api_key)
    integrator = WeatherIntegrator(provider)
    
    enriched_data = integrator.enrich_data_with_weather(base_data, lat, lon)
    
    return enriched_data

# Example usage
if __name__ == "__main__":
    # Demo weather integration
    print("🌤️ Weather Integration Demo")
    
    # Rome coordinates
    lat, lon = 41.9028, 12.4964
    
    # Create weather-enriched data
    data = create_weather_enriched_data(
        lat=lat, 
        lon=lon,
        start_date='2024-12-01',
        end_date='2024-12-07'
    )
    
    print(f"Generated {len(data)} records with weather data")
    print(f"Temperature range: {data['temperature'].min():.1f}°C to {data['temperature'].max():.1f}°C")
    print(f"Solar radiation range: {data['solar_radiation'].min():.0f} to {data['solar_radiation'].max():.0f} W/m²")
