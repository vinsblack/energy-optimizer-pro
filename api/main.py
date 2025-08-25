"""
FastAPI server for Building Energy Optimizer.
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime

# Import our optimizer
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from building_energy_optimizer.optimizer import (
    BuildingEnergyOptimizer, 
    BuildingConfig, 
    create_enhanced_example_data,
    quick_optimize
)

# Pydantic models for API
class BuildingConfigRequest(BaseModel):
    building_type: str = 'commercial'
    floor_area: float = 1000
    building_age: int = 10
    insulation_level: float = 0.7
    hvac_efficiency: float = 0.8
    occupancy_max: int = 100
    renewable_energy: bool = False

class OptimizationRequest(BaseModel):
    algorithm: str = 'xgboost'
    building_config: BuildingConfigRequest
    start_date: str
    end_date: str

class PredictionRequest(BaseModel):
    temperature: float
    humidity: float
    solar_radiation: float = 500
    wind_speed: float = 5
    precipitation: float = 0
    occupancy: float = 0.5
    hour: int
    day_of_week: int
    month: int

class OptimizationResponse(BaseModel):
    success: bool
    predictions: List[float]
    suggestions: List[Dict]
    report: Dict
    training_metrics: Dict
    model_info: Dict

class HealthResponse(BaseModel):
    status: str
    version: str
    available_algorithms: List[str]
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="Building Energy Optimizer API",
    description="Advanced ML-powered building energy optimization API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
trained_optimizers: Dict[str, BuildingEnergyOptimizer] = {}

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    available_algorithms = ['random_forest']
    
    # Check for optional dependencies
    try:
        import xgboost
        available_algorithms.append('xgboost')
    except ImportError:
        pass
    
    try:
        import lightgbm
        available_algorithms.append('lightgbm')
    except ImportError:
        pass
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        available_algorithms=available_algorithms,
        timestamp=datetime.now().isoformat()
    )

@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_building_energy(request: OptimizationRequest):
    """
    Run complete building energy optimization.
    
    This endpoint:
    1. Generates synthetic data based on date range
    2. Trains the specified ML model
    3. Generates predictions and optimization suggestions
    4. Returns comprehensive report
    """
    try:
        # Create building config
        config_dict = request.building_config.dict()
        building_config = BuildingConfig(**config_dict)
        
        # Generate enhanced data
        data = create_enhanced_example_data(
            request.start_date, 
            request.end_date, 
            building_config
        )
        
        # Run optimization
        result = quick_optimize(
            data, 
            algorithm=request.algorithm,
            building_type=request.building_config.building_type
        )
        
        # Store trained optimizer
        optimizer_id = f"{request.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trained_optimizers[optimizer_id] = result['optimizer']
        
        return OptimizationResponse(
            success=True,
            predictions=result['predictions'].tolist(),
            suggestions=result['suggestions'],
            report=result['report'],
            training_metrics=result['training_metrics'],
            model_info={
                'algorithm': request.algorithm,
                'optimizer_id': optimizer_id,
                'feature_count': len(result['optimizer'].feature_names),
                'training_samples': result['training_metrics']['training_samples']
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/predict")
async def predict_energy_consumption(
    request: PredictionRequest,
    optimizer_id: Optional[str] = None,
    algorithm: str = 'xgboost'
):
    """
    Predict energy consumption for specific conditions.
    """
    try:
        # Get or create optimizer
        if optimizer_id and optimizer_id in trained_optimizers:
            optimizer = trained_optimizers[optimizer_id]
        else:
            # Create and train a quick model
            sample_data = create_enhanced_example_data('2024-12-01', '2024-12-07')
            optimizer = BuildingEnergyOptimizer(algorithm=algorithm)
            X_scaled, y = optimizer.preprocess_data(sample_data)
            optimizer.train(X_scaled, y)
        
        # Create single prediction data point
        prediction_data = pd.DataFrame([{
            'timestamp': datetime.now(),
            'temperature': request.temperature,
            'humidity': request.humidity,
            'solar_radiation': request.solar_radiation,
            'wind_speed': request.wind_speed,
            'precipitation': request.precipitation,
            'occupancy': request.occupancy,
            'energy_consumption': 0  # Placeholder
        }])
        
        # Preprocess and predict
        X_scaled, _ = optimizer.preprocess_data(prediction_data)
        predictions, suggestions = optimizer.predict(X_scaled)
        
        return {
            "success": True,
            "predicted_consumption": float(predictions[0]),
            "conditions": request.dict(),
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/upload-data")
async def upload_energy_data(
    file: UploadFile = File(...),
    algorithm: str = 'xgboost',
    building_type: str = 'commercial'
):
    """
    Upload CSV data and get optimization results.
    """
    try:
        # Read uploaded CSV
        contents = await file.read()
        data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['timestamp', 'energy_consumption']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Run optimization on uploaded data
        result = quick_optimize(data, algorithm=algorithm, building_type=building_type)
        
        return {
            "success": True,
            "message": f"Processed {len(data)} records",
            "data_shape": data.shape,
            "columns": data.columns.tolist(),
            "optimization_results": {
                "potential_savings_percent": result['report']['summary']['potential_savings_percent'],
                "cost_savings_eur": result['report']['summary']['cost_savings_estimate_eur'],
                "suggestions_count": len(result['suggestions'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.get("/models")
async def list_trained_models():
    """List all trained models."""
    models_info = []
    for optimizer_id, optimizer in trained_optimizers.items():
        models_info.append({
            "optimizer_id": optimizer_id,
            "algorithm": optimizer.algorithm,
            "building_type": optimizer.building_config.building_type,
            "is_trained": optimizer._is_trained,
            "feature_count": len(optimizer.feature_names),
            "training_metrics": optimizer.training_metrics
        })
    
    return {
        "success": True,
        "trained_models": models_info,
        "total_models": len(models_info)
    }

@app.get("/feature-importance/{optimizer_id}")
async def get_feature_importance(optimizer_id: str):
    """Get feature importance for a trained model."""
    if optimizer_id not in trained_optimizers:
        raise HTTPException(status_code=404, detail="Optimizer not found")
    
    optimizer = trained_optimizers[optimizer_id]
    
    try:
        importance = optimizer.get_feature_importance()
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "optimizer_id": optimizer_id,
            "algorithm": optimizer.algorithm,
            "feature_importance": dict(sorted_importance),
            "top_10_features": sorted_importance[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature importance calculation failed: {str(e)}")

@app.delete("/models/{optimizer_id}")
async def delete_model(optimizer_id: str):
    """Delete a trained model from memory."""
    if optimizer_id not in trained_optimizers:
        raise HTTPException(status_code=404, detail="Optimizer not found")
    
    del trained_optimizers[optimizer_id]
    
    return {
        "success": True,
        "message": f"Model {optimizer_id} deleted successfully"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Building Energy Optimizer API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
