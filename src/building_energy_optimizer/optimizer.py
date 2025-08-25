import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import warnings

# Advanced ML models
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    warnings.warn("XGBoost not installed. Install with: pip install xgboost")

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    warnings.warn("LightGBM not installed. Install with: pip install lightgbm")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildingConfig:
    """Configuration class for building parameters."""
    
    def __init__(self, building_type: str = 'commercial', **kwargs):
        self.building_type = building_type
        self.floor_area = kwargs.get('floor_area', 1000)  # m²
        self.building_age = kwargs.get('building_age', 10)  # years
        self.insulation_level = kwargs.get('insulation_level', 0.7)  # 0-1 scale
        self.hvac_efficiency = kwargs.get('hvac_efficiency', 0.8)  # 0-1 scale
        self.occupancy_max = kwargs.get('occupancy_max', 100)  # max occupants
        self.renewable_energy = kwargs.get('renewable_energy', False)
        
    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return {
            'building_type_commercial': 1 if self.building_type == 'commercial' else 0,
            'building_type_residential': 1 if self.building_type == 'residential' else 0,
            'building_type_industrial': 1 if self.building_type == 'industrial' else 0,
            'floor_area': self.floor_area,
            'building_age': self.building_age,
            'insulation_level': self.insulation_level,
            'hvac_efficiency': self.hvac_efficiency,
            'occupancy_max': self.occupancy_max,
            'renewable_energy': 1 if self.renewable_energy else 0
        }

class BuildingEnergyOptimizer:
    """Advanced Building Energy Optimizer with multiple ML algorithms."""
    
    def __init__(self, algorithm: str = 'random_forest', building_config: Optional[BuildingConfig] = None):
        """
        Initialize the Building Energy Optimizer.
        
        Args:
            algorithm (str): ML algorithm to use ('random_forest', 'xgboost', 'lightgbm')
            building_config (BuildingConfig): Building configuration parameters
        """
        self.algorithm = algorithm
        self.building_config = building_config or BuildingConfig()
        self.scaler = StandardScaler()
        self._is_trained = False
        self.feature_names = []
        self.training_metrics = {}
        
        # Initialize model based on algorithm
        self._initialize_model()
        
        logger.info(f"Initialized optimizer with {algorithm} algorithm")

    def _initialize_model(self):
        """Initialize the ML model based on selected algorithm."""
        if self.algorithm == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.algorithm == 'xgboost' and HAS_XGBOOST:
            self.model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
        elif self.algorithm == 'lightgbm' and HAS_LIGHTGBM:
            self.model = lgb.LGBMRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        else:
            logger.warning(f"Algorithm {self.algorithm} not available, falling back to RandomForest")
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Enhanced preprocessing with more features.
        
        Args:
            data (pd.DataFrame): Raw data with enhanced feature set
            
        Returns:
            tuple: (X_scaled, y) preprocessed features and target
        """
        logger.info("Starting enhanced data preprocessing...")
        
        # Convert timestamp
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Enhanced time features
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['month'] = data['timestamp'].dt.month
        data['is_weekend'] = (data['day_of_week'] >= 5).astype(int)
        data['season'] = (data['month'] % 12 // 3 + 1)  # 1=Spring, 2=Summer, 3=Fall, 4=Winter
        
        # Working hours indicator
        data['is_working_hours'] = ((data['hour'] >= 8) & (data['hour'] <= 18) & (data['day_of_week'] < 5)).astype(int)
        
        # Weather features with defaults if missing
        weather_features = {
            'temperature': np.random.normal(22, 5, len(data)),
            'humidity': np.random.normal(50, 10, len(data)),
            'solar_radiation': np.random.uniform(0, 1000, len(data)),  # W/m²
            'wind_speed': np.random.uniform(0, 20, len(data)),  # m/s
            'precipitation': np.random.exponential(2, len(data))  # mm/h
        }
        
        for feature, default_values in weather_features.items():
            if feature not in data.columns:
                data[feature] = default_values
                logger.info(f"Added synthetic {feature} data")
        
        # Building configuration features
        building_features = self.building_config.to_dict()
        for feature, value in building_features.items():
            data[feature] = value
        
        # Occupancy features
        if 'occupancy' not in data.columns:
            # Simulate realistic occupancy patterns
            base_occupancy = np.random.uniform(0.1, 0.9, len(data))
            working_hours_boost = data['is_working_hours'] * 0.4
            weekend_reduction = (1 - data['is_weekend']) * 0.2
            data['occupancy'] = np.clip(base_occupancy + working_hours_boost - weekend_reduction, 0, 1)
        
        # Derived features
        data['cooling_degree_hours'] = np.maximum(data['temperature'] - 18, 0)
        data['heating_degree_hours'] = np.maximum(18 - data['temperature'], 0)
        data['heat_index'] = data['temperature'] + 0.5 * data['humidity'] / 100 * (data['temperature'] - 14)
        data['occupancy_load'] = data['occupancy'] * data['occupancy_max']
        data['hvac_load'] = (data['cooling_degree_hours'] + data['heating_degree_hours']) / data['hvac_efficiency']
        
        # Energy-related features
        data['base_load'] = data['floor_area'] * 0.02  # kW base load per m²
        data['lighting_load'] = data['occupancy'] * data['floor_area'] * 0.015  # kW lighting per m²
        data['equipment_load'] = data['occupancy'] * data['floor_area'] * 0.01  # kW equipment per m²
        
        # Select enhanced feature set
        self.feature_names = [
            # Weather
            'temperature', 'humidity', 'solar_radiation', 'wind_speed', 'precipitation',
            # Time
            'hour', 'day_of_week', 'month', 'is_weekend', 'season', 'is_working_hours',
            # Building config
            'building_type_commercial', 'building_type_residential', 'building_type_industrial',
            'floor_area', 'building_age', 'insulation_level', 'hvac_efficiency', 'renewable_energy',
            # Occupancy
            'occupancy', 'occupancy_max', 'occupancy_load',
            # Derived features
            'cooling_degree_hours', 'heating_degree_hours', 'heat_index', 'hvac_load',
            'base_load', 'lighting_load', 'equipment_load'
        ]
        
        X = data[self.feature_names]
        y = data['energy_consumption'].to_numpy() if 'energy_consumption' in data.columns else None
        
        # Scale features
        if not self._is_trained:
            X_scaled = self.scaler.fit_transform(X)
            logger.info(f"Fitted scaler on {X_scaled.shape[0]} samples with {X_scaled.shape[1]} features")
        else:
            X_scaled = self.scaler.transform(X)
            logger.info(f"Transformed {X_scaled.shape[0]} samples with existing scaler")
        
        return X_scaled, y

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict:
        """
        Enhanced training with validation and metrics.
        
        Args:
            X (np.ndarray): Scaled feature matrix
            y (np.ndarray): Target energy consumption values
            validation_split (float): Fraction of data for validation
            
        Returns:
            Dict: Training metrics and performance
        """
        logger.info(f"Training {self.algorithm} model...")
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self._is_trained = True
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        val_pred = self.model.predict(X_val)
        
        self.training_metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'train_r2': r2_score(y_train, train_pred),
            'val_r2': r2_score(y_val, val_pred),
            'feature_count': X.shape[1],
            'training_samples': len(X_train),
            'validation_samples': len(X_val)
        }
        
        logger.info(f"Training completed - Validation R²: {self.training_metrics['val_r2']:.3f}")
        
        return self.training_metrics
        
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Enhanced prediction with detailed optimization suggestions.
        
        Args:
            X (np.ndarray): Scaled feature matrix
            
        Returns:
            tuple: (predictions, enhanced_suggestions)
        """
        if not self._is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        predictions = self.model.predict(X)
        suggestions = self._generate_advanced_suggestions(X, predictions)
        
        logger.info(f"Generated {len(predictions)} predictions and {len(suggestions)} suggestions")
        
        return predictions, suggestions
    
    def _generate_advanced_suggestions(self, X: np.ndarray, predictions: np.ndarray) -> List[Dict]:
        """
        Generate intelligent energy optimization suggestions.
        
        Args:
            X (np.ndarray): Feature matrix
            predictions (np.ndarray): Predicted energy consumption
            
        Returns:
            List[Dict]: Detailed optimization suggestions
        """
        suggestions = []
        avg_consumption = np.mean(predictions)
        feature_dict = {name: X[:, i] for i, name in enumerate(self.feature_names)}
        
        for i, consumption in enumerate(predictions):
            if consumption > avg_consumption * 1.15:  # 15% above average
                
                suggestion = {
                    'timestamp': i,
                    'current_consumption': float(consumption),
                    'potential_savings': 0,
                    'suggestions': [],
                    'priority': 'medium'
                }
                
                # HVAC Optimization
                temp = feature_dict['temperature'][i]
                cooling_hours = feature_dict['cooling_degree_hours'][i]
                heating_hours = feature_dict['heating_degree_hours'][i]
                
                if cooling_hours > 5:  # Cooling needed
                    savings = consumption * 0.12
                    suggestion['suggestions'].append({
                        'category': 'HVAC',
                        'type': 'Cooling Optimization',
                        'action': f'Increase setpoint by 1-2°C (current: {temp:.1f}°C)',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '12%',
                        'implementation_difficulty': 'Easy'
                    })
                    suggestion['potential_savings'] += savings
                    
                elif heating_hours > 5:  # Heating needed
                    savings = consumption * 0.10
                    suggestion['suggestions'].append({
                        'category': 'HVAC',
                        'type': 'Heating Optimization',
                        'action': f'Decrease setpoint by 1-2°C (current: {temp:.1f}°C)',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '10%',
                        'implementation_difficulty': 'Easy'
                    })
                    suggestion['potential_savings'] += savings
                
                # Lighting Optimization
                hour = feature_dict['hour'][i]
                solar_rad = feature_dict['solar_radiation'][i]
                occupancy = feature_dict['occupancy'][i]
                
                if solar_rad > 500 and 8 <= hour <= 17:  # Bright daylight
                    savings = consumption * 0.08
                    suggestion['suggestions'].append({
                        'category': 'Lighting',
                        'type': 'Daylight Harvesting',
                        'action': 'Reduce artificial lighting by 40% due to high solar radiation',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '8%',
                        'implementation_difficulty': 'Medium'
                    })
                    suggestion['potential_savings'] += savings
                
                if occupancy < 0.3:  # Low occupancy
                    savings = consumption * 0.06
                    suggestion['suggestions'].append({
                        'category': 'Lighting',
                        'type': 'Occupancy Control',
                        'action': f'Reduce lighting in low-occupancy areas ({occupancy*100:.0f}% occupied)',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '6%',
                        'implementation_difficulty': 'Easy'
                    })
                    suggestion['potential_savings'] += savings
                
                # Equipment Optimization
                is_working_hours = feature_dict['is_working_hours'][i]
                is_weekend = feature_dict['is_weekend'][i]
                
                if not is_working_hours or is_weekend:
                    savings = consumption * 0.15
                    suggestion['suggestions'].append({
                        'category': 'Equipment',
                        'type': 'Standby Power Management',
                        'action': 'Switch non-essential equipment to standby mode',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '15%',
                        'implementation_difficulty': 'Medium'
                    })
                    suggestion['potential_savings'] += savings
                
                # Renewable Energy Optimization
                if self.building_config.renewable_energy and solar_rad > 700:
                    savings = consumption * 0.20
                    suggestion['suggestions'].append({
                        'category': 'Renewable',
                        'type': 'Solar Energy Utilization',
                        'action': 'Schedule energy-intensive tasks during peak solar production',
                        'estimated_savings_kwh': f"{savings:.2f}",
                        'estimated_savings_percent': '20%',
                        'implementation_difficulty': 'Hard'
                    })
                    suggestion['potential_savings'] += savings
                
                # Set priority based on potential savings
                if suggestion['potential_savings'] > consumption * 0.25:
                    suggestion['priority'] = 'high'
                elif suggestion['potential_savings'] > consumption * 0.15:
                    suggestion['priority'] = 'medium'
                else:
                    suggestion['priority'] = 'low'
                
                if suggestion['suggestions']:
                    suggestions.append(suggestion)
        
        # Sort by potential savings (highest first)
        suggestions.sort(key=lambda x: x['potential_savings'], reverse=True)
        
        return suggestions

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from the trained model.
        
        Returns:
            Dict[str, float]: Feature importance mapping
        """
        if not self._is_trained:
            raise ValueError("Model must be trained to get feature importance")
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importance = np.abs(self.model.coef_)
        else:
            return {}
        
        return dict(zip(self.feature_names, importance))

    def generate_energy_report(self, data: pd.DataFrame, predictions: np.ndarray, 
                             suggestions: List[Dict]) -> Dict:
        """
        Generate comprehensive energy report.
        
        Args:
            data (pd.DataFrame): Original data
            predictions (np.ndarray): Energy predictions
            suggestions (List[Dict]): Optimization suggestions
            
        Returns:
            Dict: Comprehensive energy report
        """
        total_consumption = np.sum(predictions)
        total_potential_savings = sum(s['potential_savings'] for s in suggestions)
        
        report = {
            'summary': {
                'total_consumption_kwh': float(total_consumption),
                'average_hourly_consumption_kwh': float(np.mean(predictions)),
                'peak_consumption_kwh': float(np.max(predictions)),
                'total_potential_savings_kwh': float(total_potential_savings),
                'potential_savings_percent': float((total_potential_savings / total_consumption) * 100),
                'cost_savings_estimate_eur': float(total_potential_savings * 0.12)  # €0.12/kWh
            },
            'time_analysis': {
                'peak_hours': self._find_peak_consumption_hours(data, predictions),
                'low_consumption_periods': self._find_low_consumption_periods(data, predictions)
            },
            'suggestions_by_category': self._categorize_suggestions(suggestions),
            'building_config': self.building_config.to_dict(),
            'model_performance': self.training_metrics
        }
        
        return report
    
    def _find_peak_consumption_hours(self, data: pd.DataFrame, predictions: np.ndarray) -> List[int]:
        """Find hours with highest energy consumption."""
        hourly_avg = data.groupby(data['timestamp'].dt.hour).apply(
            lambda x: np.mean(predictions[x.index])
        )
        return hourly_avg.nlargest(3).index.tolist()
    
    def _find_low_consumption_periods(self, data: pd.DataFrame, predictions: np.ndarray) -> List[int]:
        """Find hours with lowest energy consumption."""
        hourly_avg = data.groupby(data['timestamp'].dt.hour).apply(
            lambda x: np.mean(predictions[x.index])
        )
        return hourly_avg.nsmallest(3).index.tolist()
    
    def _categorize_suggestions(self, suggestions: List[Dict]) -> Dict:
        """Categorize suggestions by type."""
        categories = {}
        for suggestion in suggestions:
            for action in suggestion['suggestions']:
                category = action['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(action)
        
        return categories

    def save_model(self, path: str) -> None:
        """Save the complete model with enhanced metadata."""
        if not self._is_trained:
            raise ValueError("Cannot save untrained model")
            
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'algorithm': self.algorithm,
            'building_config': self.building_config.__dict__,
            'feature_names': self.feature_names,
            'training_metrics': self.training_metrics,
            'is_trained': self._is_trained,
            'version': '2.0.0',
            'created_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """Load model with enhanced metadata."""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.algorithm = model_data.get('algorithm', 'random_forest')
        self.feature_names = model_data.get('feature_names', [])
        self.training_metrics = model_data.get('training_metrics', {})
        self._is_trained = model_data['is_trained']
        
        if 'building_config' in model_data:
            config_dict = model_data['building_config']
            self.building_config = BuildingConfig(**config_dict)
        
        logger.info(f"Model loaded from {path}")

def create_enhanced_example_data(start_date: str, end_date: str, 
                               building_config: Optional[BuildingConfig] = None) -> pd.DataFrame:
    """
    Create realistic example data with enhanced features.
    
    Args:
        start_date (str): Start date for the data
        end_date (str): End date for the data
        building_config (BuildingConfig): Building configuration
        
    Returns:
        pd.DataFrame: Enhanced example dataset
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='h')
    n_samples = len(dates)
    np.random.seed(42)
    
    # Create realistic patterns
    hours = dates.hour
    days_of_week = dates.dayofweek
    months = dates.month
    
    # Temperature with seasonal variation
    base_temp = 15 + 10 * np.sin(2 * np.pi * (months - 1) / 12)  # Seasonal cycle
    daily_variation = 5 * np.sin(2 * np.pi * hours / 24)  # Daily cycle
    temperature = base_temp + daily_variation + np.random.normal(0, 2, n_samples)
    
    # Humidity inversely related to temperature
    humidity = 70 - 0.5 * temperature + np.random.normal(0, 5, n_samples)
    humidity = np.clip(humidity, 20, 90)
    
    # Solar radiation realistic pattern
    solar_base = 500 * np.maximum(np.sin(2 * np.pi * (hours - 6) / 12), 0)  # Day pattern
    seasonal_solar = 1 + 0.3 * np.sin(2 * np.pi * (months - 6) / 12)  # Seasonal
    solar_radiation = solar_base * seasonal_solar + np.random.normal(0, 50, n_samples)
    solar_radiation = np.maximum(solar_radiation, 0)
    
    # Wind speed with weather patterns
    wind_speed = np.random.exponential(5, n_samples)
    wind_speed = np.clip(wind_speed, 0, 25)
    
    # Realistic energy consumption pattern
    base_consumption = 50  # Base load
    
    # HVAC load based on temperature
    hvac_load = 30 * (np.maximum(temperature - 22, 0) + np.maximum(18 - temperature, 0))
    
    # Occupancy patterns
    is_working_hours = ((hours >= 8) & (hours <= 18) & (days_of_week < 5))
    occupancy_factor = np.where(is_working_hours, 0.7, 0.2)
    occupancy_factor = np.where(days_of_week >= 5, occupancy_factor * 0.3, occupancy_factor)
    occupancy = occupancy_factor + np.random.normal(0, 0.1, n_samples)
    occupancy = np.clip(occupancy, 0, 1)
    
    # Lighting load
    lighting_load = 20 * occupancy * np.maximum(1 - solar_radiation / 500, 0.2)
    
    # Equipment load
    equipment_load = 15 * occupancy
    
    # Total consumption
    energy_consumption = (base_consumption + hvac_load + lighting_load + equipment_load + 
                         np.random.normal(0, 5, n_samples))
    energy_consumption = np.maximum(energy_consumption, 10)  # Minimum consumption
    
    data = pd.DataFrame({
        'timestamp': dates,
        'temperature': temperature,
        'humidity': humidity,
        'solar_radiation': solar_radiation,
        'wind_speed': wind_speed,
        'precipitation': np.random.exponential(0.5, n_samples),
        'occupancy': occupancy,
        'energy_consumption': energy_consumption
    })
    
    return data

# Convenience function for quick optimization
def quick_optimize(data: pd.DataFrame, algorithm: str = 'xgboost', 
                  building_type: str = 'commercial') -> Dict:
    """
    Quick optimization function for immediate results.
    
    Args:
        data (pd.DataFrame): Building energy data
        algorithm (str): ML algorithm to use
        building_type (str): Type of building
        
    Returns:
        Dict: Complete optimization results
    """
    config = BuildingConfig(building_type=building_type)
    optimizer = BuildingEnergyOptimizer(algorithm=algorithm, building_config=config)
    
    # Preprocess and train
    X_scaled, y = optimizer.preprocess_data(data)
    metrics = optimizer.train(X_scaled, y)
    
    # Generate predictions and suggestions
    predictions, suggestions = optimizer.predict(X_scaled)
    
    # Generate report
    report = optimizer.generate_energy_report(data, predictions, suggestions)
    
    return {
        'optimizer': optimizer,
        'predictions': predictions,
        'suggestions': suggestions,
        'report': report,
        'training_metrics': metrics
    }
