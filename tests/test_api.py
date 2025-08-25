"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import json
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test all API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "available_algorithms" in data
        assert "timestamp" in data
        assert isinstance(data["available_algorithms"], list)
    
    def test_optimize_endpoint(self):
        """Test complete optimization endpoint."""
        request_data = {
            "algorithm": "random_forest",
            "building_config": {
                "building_type": "commercial",
                "floor_area": 2000,
                "building_age": 8,
                "insulation_level": 0.75,
                "hvac_efficiency": 0.85,
                "occupancy_max": 120,
                "renewable_energy": True
            },
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        }
        
        response = client.post("/optimize", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "predictions" in data
        assert "suggestions" in data
        assert "report" in data
        assert "training_metrics" in data
        assert "model_info" in data
        
        # Check report structure
        report = data["report"]
        assert "summary" in report
        assert "total_consumption_kwh" in report["summary"]
        assert "potential_savings_percent" in report["summary"]
    
    def test_predict_endpoint(self):
        """Test single prediction endpoint."""
        request_data = {
            "temperature": 25.0,
            "humidity": 60.0,
            "solar_radiation": 800.0,
            "wind_speed": 5.0,
            "precipitation": 0.0,
            "occupancy": 0.7,
            "hour": 14,
            "day_of_week": 2,
            "month": 6
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "predicted_consumption" in data
        assert isinstance(data["predicted_consumption"], float)
        assert data["predicted_consumption"] > 0
    
    def test_models_endpoint(self):
        """Test models listing endpoint."""
        # First run an optimization to create a model
        self.test_optimize_endpoint()
        
        response = client.get("/models")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "trained_models" in data
        assert "total_models" in data
    
    def test_upload_data_endpoint(self):
        """Test data upload endpoint."""
        # Create sample CSV data
        dates = pd.date_range('2024-01-01', periods=48, freq='h')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'energy_consumption': np.random.normal(100, 15, len(dates)),
            'temperature': np.random.normal(20, 5, len(dates)),
            'humidity': np.random.normal(50, 10, len(dates))
        })
        
        csv_content = sample_data.to_csv(index=False)
        
        # Upload file
        files = {"file": ("test_data.csv", csv_content, "text/csv")}
        data = {"algorithm": "random_forest", "building_type": "commercial"}
        
        response = client.post("/upload-data", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "optimization_results" in result
        assert "potential_savings_percent" in result["optimization_results"]
    
    def test_invalid_optimization_request(self):
        """Test error handling for invalid optimization request."""
        invalid_request = {
            "algorithm": "invalid_algorithm",
            "building_config": {
                "building_type": "invalid_type"
            },
            "start_date": "invalid_date",
            "end_date": "2024-01-07"
        }
        
        response = client.post("/optimize", json=invalid_request)
        assert response.status_code == 500  # Should return error
    
    def test_feature_importance_endpoint(self):
        """Test feature importance endpoint."""
        # First create a model
        self.test_optimize_endpoint()
        
        # Get models to find an optimizer_id
        models_response = client.get("/models")
        models_data = models_response.json()
        
        if models_data["trained_models"]:
            optimizer_id = models_data["trained_models"][0]["optimizer_id"]
            
            response = client.get(f"/feature-importance/{optimizer_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "feature_importance" in data
            assert "top_10_features" in data
        else:
            pytest.skip("No trained models available for feature importance test")

class TestAPIPerformance:
    """Test API performance and scalability."""
    
    def test_optimization_performance(self):
        """Test optimization endpoint performance."""
        request_data = {
            "algorithm": "random_forest",
            "building_config": {
                "building_type": "commercial",
                "floor_area": 5000,  # Larger building
                "building_age": 5,
                "insulation_level": 0.8,
                "hvac_efficiency": 0.9,
                "occupancy_max": 300,
                "renewable_energy": True
            },
            "start_date": "2024-01-01",
            "end_date": "2024-01-30"  # Month of data
        }
        
        start_time = datetime.now()
        response = client.post("/optimize", json=request_data)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        assert processing_time < 60  # Should complete within 1 minute
        
        print(f"API Performance: Large optimization completed in {processing_time:.2f}s")
    
    def test_prediction_performance(self):
        """Test prediction endpoint performance."""
        request_data = {
            "temperature": 22.0,
            "humidity": 55.0,
            "solar_radiation": 600.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "occupancy": 0.6,
            "hour": 12,
            "day_of_week": 1,
            "month": 6
        }
        
        # Run multiple predictions to test consistency
        response_times = []
        for _ in range(5):
            start_time = datetime.now()
            response = client.post("/predict", json=request_data)
            response_time = (datetime.now() - start_time).total_seconds()
            response_times.append(response_time)
            
            assert response.status_code == 200
        
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 5  # Should be very fast
        
        print(f"API Performance: Average prediction time: {avg_response_time:.3f}s")

class TestAPIErrorHandling:
    """Test API error handling scenarios."""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_request = {
            "algorithm": "random_forest",
            # Missing building_config and dates
        }
        
        response = client.post("/optimize", json=incomplete_request)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types."""
        invalid_request = {
            "algorithm": "random_forest",
            "building_config": {
                "building_type": "commercial",
                "floor_area": "not_a_number",  # Should be float
                "building_age": 8,
                "insulation_level": 0.75,
                "hvac_efficiency": 0.85,
                "occupancy_max": 120,
                "renewable_energy": True
            },
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        }
        
        response = client.post("/optimize", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_feature_importance_not_found(self):
        """Test feature importance endpoint with non-existent model."""
        response = client.get("/feature-importance/non_existent_id")
        assert response.status_code == 404
        
        data = response.json()
        assert "Optimizer not found" in data["detail"]

# Utility functions for testing
def create_test_csv() -> str:
    """Create a test CSV file for upload testing."""
    dates = pd.date_range('2024-01-01', periods=168, freq='h')  # 1 week
    test_data = pd.DataFrame({
        'timestamp': dates,
        'energy_consumption': np.random.normal(100, 20, len(dates)),
        'temperature': np.random.normal(20, 8, len(dates)),
        'humidity': np.random.normal(50, 15, len(dates)),
        'occupancy': np.random.uniform(0, 1, len(dates))
    })
    
    return test_data.to_csv(index=False)

if __name__ == "__main__":
    # Run API tests
    print("🧪 Running API Tests...")
    pytest.main([__file__, "-v", "--tb=short"])
