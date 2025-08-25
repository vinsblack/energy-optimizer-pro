import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from building_energy_optimizer.optimizer import BuildingEnergyOptimizer, create_example_data

def test_optimizer_initialization():
    """Test if the optimizer initializes correctly."""
    optimizer = BuildingEnergyOptimizer()
    assert optimizer.model is not None
    assert optimizer.scaler is not None
    assert not optimizer._is_trained

def test_data_preprocessing():
    """Test data preprocessing functionality."""
    # Create sample data
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    data = create_example_data(start_date.strftime('%Y-%m-%d'), 
                             end_date.strftime('%Y-%m-%d'))
    
    optimizer = BuildingEnergyOptimizer()
    X_scaled, y = optimizer.preprocess_data(data)
    
    # Check shapes and types
    assert isinstance(X_scaled, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert len(X_scaled) == len(y)
    assert X_scaled.shape[1] == 6  # number of features

def test_model_training():
    """Test model training process."""
    optimizer = BuildingEnergyOptimizer()
    
    # Create and preprocess sample data
    data = create_example_data('2024-01-01', '2024-01-07')
    X_scaled, y = optimizer.preprocess_data(data)
    
    # Train model
    optimizer.train(X_scaled, y)
    assert optimizer._is_trained
    
    # Try prediction
    predictions, suggestions = optimizer.predict(X_scaled)
    assert len(predictions) == len(X_scaled)
    assert isinstance(suggestions, list)

def test_optimization_suggestions():
    """Test if optimization suggestions are generated correctly."""
    optimizer = BuildingEnergyOptimizer()
    
    # Create and preprocess sample data
    data = create_example_data('2024-01-01', '2024-01-07')
    X_scaled, y = optimizer.preprocess_data(data)
    
    # Train and predict
    optimizer.train(X_scaled, y)
    predictions, suggestions = optimizer.predict(X_scaled)
    
    # Check suggestions format
    for suggestion in suggestions:
        assert 'timestamp' in suggestion
        assert 'current_consumption' in suggestion
        assert 'suggestions' in suggestion
        
        # Check individual suggestions
        for action in suggestion['suggestions']:
            assert 'type' in action
            assert 'action' in action
            assert 'estimated_savings' in action

def test_model_save_load(tmp_path):
    """Test model saving and loading functionality."""
    optimizer = BuildingEnergyOptimizer()
    
    # Train model
    data = create_example_data('2024-01-01', '2024-01-07')
    X_scaled, y = optimizer.preprocess_data(data)
    optimizer.train(X_scaled, y)
    
    # Save model
    model_path = tmp_path / "model.joblib"
    optimizer.save_model(str(model_path))
    assert model_path.exists()
    
    # Load model in new instance
    new_optimizer = BuildingEnergyOptimizer()
    new_optimizer.load_model(str(model_path))
    assert new_optimizer._is_trained
    
    # Verify predictions match
    pred1, _ = optimizer.predict(X_scaled)
    pred2, _ = new_optimizer.predict(X_scaled)
    np.testing.assert_array_almost_equal(pred1, pred2)

def test_error_handling():
    """Test error handling in the optimizer."""
    optimizer = BuildingEnergyOptimizer()
    
    # Test prediction without training
    with pytest.raises(ValueError, match="Model must be trained before making predictions"):
        X = np.random.rand(10, 6)
        optimizer.predict(X)
    
    # Test saving untrained model
    with pytest.raises(ValueError, match="Cannot save untrained model"):
        optimizer.save_model("test_model.joblib")
