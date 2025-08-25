"""
Comprehensive tests for Building Energy Optimizer v2.0
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from building_energy_optimizer.optimizer import (
    BuildingEnergyOptimizer, 
    BuildingConfig, 
    create_enhanced_example_data,
    quick_optimize
)
from building_energy_optimizer.utils.database import DatabaseManager, init_database
from building_energy_optimizer.utils.weather import OpenWeatherMapProvider, WeatherIntegrator

class TestBuildingConfig:
    """Test BuildingConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = BuildingConfig()
        assert config.building_type == 'commercial'
        assert config.floor_area == 1000
        assert config.building_age == 10
        assert config.insulation_level == 0.7
        assert config.hvac_efficiency == 0.8
        assert config.occupancy_max == 100
        assert not config.renewable_energy
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = BuildingConfig(
            building_type='residential',
            floor_area=250,
            renewable_energy=True
        )
        assert config.building_type == 'residential'
        assert config.floor_area == 250
        assert config.renewable_energy
    
    def test_config_to_dict(self):
        """Test configuration to dictionary conversion."""
        config = BuildingConfig(building_type='industrial')
        config_dict = config.to_dict()
        
        assert 'building_type_industrial' in config_dict
        assert config_dict['building_type_industrial'] == 1
        assert config_dict['building_type_commercial'] == 0
        assert 'floor_area' in config_dict
        assert 'renewable_energy' in config_dict

class TestBuildingEnergyOptimizer:
    """Test enhanced BuildingEnergyOptimizer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return create_enhanced_example_data('2024-01-01', '2024-01-07')
    
    @pytest.fixture
    def building_config(self):
        """Create test building configuration."""
        return BuildingConfig(
            building_type='commercial',
            floor_area=2000,
            renewable_energy=True
        )
    
    def test_optimizer_initialization_default(self):
        """Test default optimizer initialization."""
        optimizer = BuildingEnergyOptimizer()
        assert optimizer.algorithm == 'random_forest'
        assert optimizer.building_config is not None
        assert not optimizer._is_trained
        assert optimizer.feature_names == []
    
    def test_optimizer_initialization_custom(self, building_config):
        """Test custom optimizer initialization."""
        optimizer = BuildingEnergyOptimizer(
            algorithm='xgboost',
            building_config=building_config
        )
        assert optimizer.algorithm == 'xgboost'
        assert optimizer.building_config.building_type == 'commercial'
        assert optimizer.building_config.floor_area == 2000
    
    def test_enhanced_preprocessing(self, sample_data, building_config):
        """Test enhanced data preprocessing."""
        optimizer = BuildingEnergyOptimizer(building_config=building_config)
        X_scaled, y = optimizer.preprocess_data(sample_data)
        
        # Check output format
        assert isinstance(X_scaled, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert len(X_scaled) == len(y)
        assert len(X_scaled) == len(sample_data)
        
        # Check feature count (should be much more than original 6)
        assert X_scaled.shape[1] > 20  # Enhanced feature set
        assert len(optimizer.feature_names) == X_scaled.shape[1]
        
        # Check feature names
        expected_features = [
            'temperature', 'humidity', 'solar_radiation', 'wind_speed',
            'hour', 'day_of_week', 'month', 'is_weekend', 'season',
            'building_type_commercial', 'floor_area', 'renewable_energy',
            'occupancy', 'cooling_degree_hours', 'heating_degree_hours'
        ]
        
        for feature in expected_features:
            assert feature in optimizer.feature_names
    
    def test_multiple_algorithms(self, sample_data):
        """Test different ML algorithms."""
        algorithms = ['random_forest', 'xgboost', 'lightgbm']
        
        for algorithm in algorithms:
            optimizer = BuildingEnergyOptimizer(algorithm=algorithm)
            X_scaled, y = optimizer.preprocess_data(sample_data.copy())
            
            # Should not raise exception
            try:
                metrics = optimizer.train(X_scaled, y)
                assert optimizer._is_trained
                assert 'val_r2' in metrics
                assert 'val_mae' in metrics
                assert metrics['val_r2'] >= 0  # R² should be reasonable
                
                # Test prediction
                predictions, suggestions = optimizer.predict(X_scaled)
                assert len(predictions) == len(X_scaled)
                assert isinstance(suggestions, list)
                
            except ImportError:
                # Algorithm not available, skip
                pytest.skip(f"{algorithm} not installed")
    
    def test_advanced_suggestions(self, sample_data, building_config):
        """Test advanced optimization suggestions."""
        optimizer = BuildingEnergyOptimizer(
            algorithm='random_forest',
            building_config=building_config
        )
        
        X_scaled, y = optimizer.preprocess_data(sample_data)
        optimizer.train(X_scaled, y)
        predictions, suggestions = optimizer.predict(X_scaled)
        
        # Check suggestions structure
        for suggestion in suggestions:
            assert 'timestamp' in suggestion
            assert 'current_consumption' in suggestion
            assert 'potential_savings' in suggestion
            assert 'priority' in suggestion
            assert 'suggestions' in suggestion
            assert suggestion['priority'] in ['low', 'medium', 'high']
            
            # Check individual actions
            for action in suggestion['suggestions']:
                required_keys = ['category', 'type', 'action', 'estimated_savings_kwh', 
                               'estimated_savings_percent', 'implementation_difficulty']
                for key in required_keys:
                    assert key in action
                
                assert action['category'] in ['HVAC', 'Lighting', 'Equipment', 'Renewable']
                assert action['implementation_difficulty'] in ['Easy', 'Medium', 'Hard']
    
    def test_feature_importance(self, sample_data):
        """Test feature importance extraction."""
        optimizer = BuildingEnergyOptimizer()
        X_scaled, y = optimizer.preprocess_data(sample_data)
        optimizer.train(X_scaled, y)
        
        importance = optimizer.get_feature_importance()
        
        assert isinstance(importance, dict)
        assert len(importance) == len(optimizer.feature_names)
        
        # All importance values should be non-negative
        for feature, score in importance.items():
            assert score >= 0
            assert feature in optimizer.feature_names
    
    def test_energy_report_generation(self, sample_data, building_config):
        """Test comprehensive energy report generation."""
        optimizer = BuildingEnergyOptimizer(building_config=building_config)
        X_scaled, y = optimizer.preprocess_data(sample_data)
        optimizer.train(X_scaled, y)
        predictions, suggestions = optimizer.predict(X_scaled)
        
        report = optimizer.generate_energy_report(sample_data, predictions, suggestions)
        
        # Check report structure
        assert 'summary' in report
        assert 'time_analysis' in report
        assert 'suggestions_by_category' in report
        assert 'building_config' in report
        assert 'model_performance' in report
        
        # Check summary metrics
        summary = report['summary']
        required_metrics = [
            'total_consumption_kwh', 'average_hourly_consumption_kwh',
            'peak_consumption_kwh', 'total_potential_savings_kwh',
            'potential_savings_percent', 'cost_savings_estimate_eur'
        ]
        
        for metric in required_metrics:
            assert metric in summary
            assert isinstance(summary[metric], (int, float))
            assert summary[metric] >= 0
    
    def test_model_save_load_enhanced(self, sample_data, tmp_path):
        """Test enhanced model saving and loading."""
        optimizer = BuildingEnergyOptimizer(algorithm='random_forest')
        X_scaled, y = optimizer.preprocess_data(sample_data)
        optimizer.train(X_scaled, y)
        
        # Save model
        model_path = tmp_path / "enhanced_model.joblib"
        optimizer.save_model(str(model_path))
        assert model_path.exists()
        
        # Load model in new instance
        new_optimizer = BuildingEnergyOptimizer()
        new_optimizer.load_model(str(model_path))
        
        # Verify all attributes loaded correctly
        assert new_optimizer._is_trained
        assert new_optimizer.algorithm == 'random_forest'
        assert len(new_optimizer.feature_names) == len(optimizer.feature_names)
        assert new_optimizer.training_metrics == optimizer.training_metrics
        
        # Verify predictions match
        pred1, _ = optimizer.predict(X_scaled)
        pred2, _ = new_optimizer.predict(X_scaled)
        np.testing.assert_array_almost_equal(pred1, pred2)

class TestQuickOptimize:
    """Test quick_optimize convenience function."""
    
    def test_quick_optimize_basic(self):
        """Test basic quick optimization."""
        data = create_enhanced_example_data('2024-01-01', '2024-01-03')
        
        result = quick_optimize(data, algorithm='random_forest', building_type='commercial')
        
        # Check result structure
        assert 'optimizer' in result
        assert 'predictions' in result
        assert 'suggestions' in result
        assert 'report' in result
        assert 'training_metrics' in result
        
        # Check optimizer is trained
        assert result['optimizer']._is_trained
        
        # Check predictions
        assert len(result['predictions']) == len(data)
        
        # Check report completeness
        assert 'summary' in result['report']
        assert 'potential_savings_percent' in result['report']['summary']

class TestWeatherIntegration:
    """Test weather integration functionality."""
    
    def test_weather_provider_synthetic(self):
        """Test synthetic weather data generation."""
        provider = OpenWeatherMapProvider()  # No API key - should use synthetic
        
        weather = provider.get_current_weather(41.9028, 12.4964)
        
        assert hasattr(weather, 'temperature')
        assert hasattr(weather, 'humidity')
        assert hasattr(weather, 'solar_radiation')
        assert hasattr(weather, 'wind_speed')
        assert hasattr(weather, 'precipitation')
        
        # Check reasonable ranges
        assert -20 <= weather.temperature <= 50
        assert 0 <= weather.humidity <= 100
        assert 0 <= weather.solar_radiation <= 1200
        assert 0 <= weather.wind_speed <= 50
    
    def test_weather_forecast(self):
        """Test weather forecast generation."""
        provider = OpenWeatherMapProvider()
        forecast = provider.get_forecast(41.9028, 12.4964, hours=24)
        
        assert len(forecast) > 0
        assert all(hasattr(w, 'temperature') for w in forecast)
        assert all(hasattr(w, 'timestamp') for w in forecast)
    
    def test_weather_integration(self):
        """Test weather data integration with building data."""
        # Create basic building data
        dates = pd.date_range('2024-01-01', periods=48, freq='h')
        base_data = pd.DataFrame({
            'timestamp': dates,
            'energy_consumption': np.random.normal(100, 20, len(dates))
        })
        
        provider = OpenWeatherMapProvider()
        integrator = WeatherIntegrator(provider)
        
        enriched_data = integrator.enrich_data_with_weather(base_data, 41.9, 12.5)
        
        # Check weather columns added
        weather_columns = ['temperature', 'humidity', 'solar_radiation', 'wind_speed', 'precipitation']
        for col in weather_columns:
            assert col in enriched_data.columns
        
        assert len(enriched_data) == len(base_data)

class TestDatabaseIntegration:
    """Test database integration functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_url = f"sqlite:///{tmp.name}"
            db_manager = DatabaseManager(db_url)
            yield db_manager
            
            # Cleanup
            try:
                os.unlink(tmp.name)
            except:
                pass
    
    def test_database_initialization(self, temp_db):
        """Test database initialization."""
        assert temp_db.engine is not None
        assert temp_db.SessionLocal is not None
    
    def test_building_crud(self, temp_db):
        """Test building CRUD operations."""
        # Create building
        building_data = {
            'name': 'Test Building',
            'building_type': 'commercial',
            'floor_area': 1500,
            'building_age': 5,
            'insulation_level': 0.8,
            'hvac_efficiency': 0.9,
            'occupancy_max': 80,
            'renewable_energy': True
        }
        
        building = temp_db.create_building(building_data)
        assert building.id is not None
        assert building.name == 'Test Building'
        assert building.renewable_energy is True
        
        # Get building
        retrieved = temp_db.get_building(building.id)
        assert retrieved is not None
        assert retrieved.name == building.name
        
        # Get all buildings
        all_buildings = temp_db.get_buildings()
        assert len(all_buildings) >= 1
    
    def test_energy_data_storage(self, temp_db):
        """Test energy data storage and retrieval."""
        # Create building first
        building = temp_db.create_building({
            'name': 'Test Building',
            'building_type': 'commercial',
            'floor_area': 1000,
            'building_age': 10,
            'insulation_level': 0.7,
            'hvac_efficiency': 0.8,
            'occupancy_max': 100,
            'renewable_energy': False
        })
        
        # Create sample energy data
        dates = pd.date_range('2024-01-01', periods=24, freq='h')
        energy_data = pd.DataFrame({
            'timestamp': dates,
            'energy_consumption': np.random.normal(100, 10, len(dates)),
            'temperature': np.random.normal(20, 5, len(dates)),
            'humidity': np.random.normal(50, 10, len(dates)),
            'occupancy': np.random.uniform(0, 1, len(dates))
        })
        
        # Save data
        records_saved = temp_db.save_energy_data(building.id, energy_data)
        assert records_saved == len(energy_data)
        
        # Retrieve data
        retrieved_data = temp_db.get_energy_data(building.id)
        assert len(retrieved_data) == len(energy_data)
        assert 'energy_consumption' in retrieved_data.columns
        assert 'temperature' in retrieved_data.columns
    
    def test_optimization_result_storage(self, temp_db):
        """Test optimization result storage."""
        # Create building
        building = temp_db.create_building({
            'name': 'Test Building',
            'building_type': 'commercial',
            'floor_area': 1000,
            'building_age': 10,
            'insulation_level': 0.7,
            'hvac_efficiency': 0.8,
            'occupancy_max': 100,
            'renewable_energy': False
        })
        
        # Mock optimization results
        metrics = {
            'val_r2': 0.85,
            'val_mae': 10.5,
            'training_samples': 500
        }
        
        report = {
            'summary': {
                'total_consumption_kwh': 1000.0,
                'total_potential_savings_kwh': 150.0,
                'potential_savings_percent': 15.0,
                'cost_savings_estimate_eur': 18.0
            }
        }
        
        suggestions = [{'test': 'suggestion'}]
        feature_importance = {'temperature': 0.3, 'occupancy': 0.2}
        
        # Save result
        result = temp_db.save_optimization_result(
            building.id, 'xgboost', metrics, report, suggestions, feature_importance
        )
        
        assert result.id is not None
        assert result.algorithm == 'xgboost'
        assert result.validation_r2 == 0.85
        assert result.potential_savings_percent == 15.0

class TestEnhancedDataGeneration:
    """Test enhanced data generation functions."""
    
    def test_enhanced_data_generation(self):
        """Test enhanced example data generation."""
        data = create_enhanced_example_data('2024-01-01', '2024-01-07')
        
        # Check basic structure
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert 'timestamp' in data.columns
        assert 'energy_consumption' in data.columns
        
        # Check enhanced features
        expected_columns = [
            'temperature', 'humidity', 'solar_radiation', 'wind_speed',
            'precipitation', 'occupancy', 'energy_consumption'
        ]
        
        for col in expected_columns:
            assert col in data.columns
        
        # Check data quality
        assert data['temperature'].min() > -40  # Reasonable temperature range
        assert data['temperature'].max() < 60
        assert data['humidity'].min() >= 0
        assert data['humidity'].max() <= 100
        assert data['solar_radiation'].min() >= 0
        assert data['occupancy'].min() >= 0
        assert data['occupancy'].max() <= 1
        assert data['energy_consumption'].min() > 0
    
    def test_realistic_patterns(self):
        """Test that generated data has realistic patterns."""
        data = create_enhanced_example_data('2024-06-01', '2024-06-07')  # Summer data
        
        # Check for daily temperature patterns
        daily_temp_var = data.groupby(data['timestamp'].dt.date)['temperature'].std()
        assert daily_temp_var.mean() > 2  # Should have daily variation
        
        # Check for solar radiation patterns (should be 0 at night)
        night_hours = data[data['timestamp'].dt.hour.isin([0, 1, 2, 3, 4, 5])]
        assert night_hours['solar_radiation'].max() < 100  # Low solar at night
        
        # Check occupancy patterns (should be lower on weekends)
        weekday_occupancy = data[data['timestamp'].dt.dayofweek < 5]['occupancy'].mean()
        weekend_occupancy = data[data['timestamp'].dt.dayofweek >= 5]['occupancy'].mean()
        assert weekday_occupancy > weekend_occupancy  # Higher occupancy on weekdays

class TestIntegrationWorkflow:
    """Test complete integration workflow."""
    
    def test_complete_workflow(self):
        """Test complete optimization workflow."""
        # This test covers the entire pipeline
        
        # 1. Generate data
        data = create_enhanced_example_data('2024-01-01', '2024-01-14')
        assert len(data) > 0
        
        # 2. Quick optimization
        result = quick_optimize(data, algorithm='random_forest', building_type='commercial')
        
        # 3. Verify all components
        assert 'optimizer' in result
        assert 'predictions' in result
        assert 'suggestions' in result
        assert 'report' in result
        assert 'training_metrics' in result
        
        # 4. Check optimizer functionality
        optimizer = result['optimizer']
        assert optimizer._is_trained
        assert len(optimizer.feature_names) > 20
        
        # 5. Check predictions quality
        predictions = result['predictions']
        actual = data['energy_consumption'].values
        
        # R² should be reasonable (>0.5 for synthetic data)
        r2 = result['training_metrics']['val_r2']
        assert r2 > 0.5
        
        # 6. Check suggestions quality
        suggestions = result['suggestions']
        if suggestions:  # May be empty if no high consumption periods
            assert isinstance(suggestions, list)
            assert all('potential_savings' in s for s in suggestions)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        optimizer = BuildingEnergyOptimizer()
        
        # Test prediction without training
        with pytest.raises(ValueError, match="Model must be trained"):
            X = np.random.rand(10, 25)
            optimizer.predict(X)
        
        # Test saving untrained model
        with pytest.raises(ValueError, match="Cannot save untrained model"):
            optimizer.save_model("test.joblib")
        
        # Test feature importance without training
        with pytest.raises(ValueError, match="Model must be trained"):
            optimizer.get_feature_importance()

# Performance benchmarks
class TestPerformance:
    """Performance and benchmark tests."""
    
    def test_training_speed(self):
        """Test training speed with large dataset."""
        # Generate larger dataset
        data = create_enhanced_example_data('2024-01-01', '2024-03-31')  # 3 months
        
        optimizer = BuildingEnergyOptimizer(algorithm='random_forest')
        
        start_time = datetime.now()
        X_scaled, y = optimizer.preprocess_data(data)
        preprocessing_time = (datetime.now() - start_time).total_seconds()
        
        start_time = datetime.now()
        optimizer.train(X_scaled, y)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete in reasonable time
        assert preprocessing_time < 30  # seconds
        assert training_time < 120     # seconds
        
        print(f"Performance: Preprocessing {len(data)} records: {preprocessing_time:.2f}s")
        print(f"Performance: Training: {training_time:.2f}s")
    
    def test_prediction_speed(self):
        """Test prediction speed."""
        data = create_enhanced_example_data('2024-01-01', '2024-01-07')
        
        optimizer = BuildingEnergyOptimizer()
        X_scaled, y = optimizer.preprocess_data(data)
        optimizer.train(X_scaled, y)
        
        start_time = datetime.now()
        predictions, suggestions = optimizer.predict(X_scaled)
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        # Should be very fast
        assert prediction_time < 5  # seconds
        
        print(f"Performance: Prediction for {len(data)} records: {prediction_time:.3f}s")

if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__ + "::TestBuildingEnergyOptimizer::test_enhanced_preprocessing", "-v"])
