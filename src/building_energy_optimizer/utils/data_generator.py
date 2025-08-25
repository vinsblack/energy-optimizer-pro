"""
Data generator utilities for Building Energy Optimizer.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def create_enhanced_example_data(start_date: str, end_date: str, 
                                building_type: str = "commercial",
                                floor_area: float = 2500.0) -> pd.DataFrame:
    """
    Generate comprehensive synthetic energy consumption data.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        building_type: Type of building ('residential', 'commercial', 'industrial')
        floor_area: Floor area in square meters
    
    Returns:
        DataFrame with synthetic energy data and features
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") 
    hours = int((end - start).total_seconds() / 3600)
    
    if hours <= 0:
        raise ValueError("End date must be after start date")
    
    # Generate timestamps
    timestamps = [start + timedelta(hours=i) for i in range(hours)]
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Base consumption patterns by building type
    base_patterns = {
        'residential': {'base': 30, 'amplitude': 15, 'noise': 3},
        'commercial': {'base': 50, 'amplitude': 25, 'noise': 5},
        'industrial': {'base': 100, 'amplitude': 40, 'noise': 8}
    }
    
    pattern = base_patterns.get(building_type, base_patterns['commercial'])
    
    # Generate realistic energy consumption patterns
    hours_array = np.arange(hours)
    
    # Daily pattern (higher during day for commercial, opposite for residential)
    daily_pattern = np.sin(hours_array * 2 * np.pi / 24)
    if building_type == 'residential':
        daily_pattern = -daily_pattern  # Peak in evening/morning
    
    # Weekly pattern (lower on weekends for commercial)
    weekly_pattern = np.sin(hours_array * 2 * np.pi / (24 * 7))
    if building_type in ['commercial', 'industrial']:
        weekly_pattern *= 0.3  # Reduce weekend consumption
    
    # Base consumption
    base_consumption = pattern['base'] * (floor_area / 2500.0)  # Scale by area
    
    # Combine patterns
    consumption = (
        base_consumption + 
        pattern['amplitude'] * daily_pattern +
        pattern['amplitude'] * 0.2 * weekly_pattern +
        np.random.normal(0, pattern['noise'], hours)
    )
    
    # Ensure realistic bounds
    consumption = np.clip(consumption, 5, 300)
    
    # Generate weather data
    base_temp = 20  # Base temperature
    temp_variation = np.sin(hours_array * 2 * np.pi / (24 * 365.25)) * 15  # Seasonal
    daily_temp_var = np.sin(hours_array * 2 * np.pi / 24) * 5  # Daily variation
    temperature = base_temp + temp_variation + daily_temp_var + np.random.normal(0, 2, hours)
    
    humidity = 50 + np.random.normal(0, 10, hours)
    humidity = np.clip(humidity, 20, 95)
    
    # Generate additional features
    data = pd.DataFrame({
        'timestamp': timestamps,
        'energy_consumption': consumption,
        'temperature': temperature,
        'humidity': humidity,
        'hour': [t.hour for t in timestamps],
        'day_of_week': [t.weekday() for t in timestamps],
        'is_weekend': [1 if t.weekday() >= 5 else 0 for t in timestamps],
        'month': [t.month for t in timestamps],
        'is_business_hours': [1 if 8 <= t.hour <= 18 and t.weekday() < 5 else 0 for t in timestamps]
    })
    
    # Add building-specific features
    data['building_type'] = building_type
    data['floor_area'] = floor_area
    data['energy_per_sqm'] = data['energy_consumption'] / floor_area
    
    # Add some derived features
    data['temp_difference'] = data['temperature'] - 20  # Difference from comfort temperature
    data['cooling_degree_hours'] = np.maximum(0, data['temperature'] - 24)
    data['heating_degree_hours'] = np.maximum(0, 18 - data['temperature'])
    
    return data

def create_building_config_data(building_type: str = "commercial", 
                               floor_area: float = 2500.0) -> Dict[str, Any]:
    """Generate building configuration data."""
    
    configs = {
        'residential': {
            'typical_occupants': max(1, int(floor_area / 50)),
            'hvac_efficiency': 0.85,
            'insulation_rating': 'medium',
            'appliance_count': max(5, int(floor_area / 100))
        },
        'commercial': {
            'typical_occupants': max(10, int(floor_area / 20)),
            'hvac_efficiency': 0.75,
            'insulation_rating': 'high',
            'equipment_density': floor_area / 10  # W/m²
        },
        'industrial': {
            'typical_occupants': max(5, int(floor_area / 100)),
            'hvac_efficiency': 0.65,
            'insulation_rating': 'low',
            'process_equipment_power': floor_area * 50  # High power density
        }
    }
    
    base_config = {
        'building_type': building_type,
        'floor_area': floor_area,
        'construction_year': 2010,
        'energy_rating': 'B'
    }
    
    specific_config = configs.get(building_type, configs['commercial'])
    base_config.update(specific_config)
    
    return base_config

def generate_synthetic_data(hours: int = 168) -> pd.DataFrame:
    """Generate synthetic data for specified hours (backward compatibility)."""
    start_date = "2024-01-01"
    end_date = (datetime(2024, 1, 1) + timedelta(hours=hours)).strftime("%Y-%m-%d")
    return create_enhanced_example_data(start_date, end_date)

__all__ = [
    'create_enhanced_example_data',
    'create_building_config_data',
    'generate_synthetic_data'
]