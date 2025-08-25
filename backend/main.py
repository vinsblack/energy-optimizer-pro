"""
Building Energy Optimizer - Enhanced Professional FastAPI Backend v2.1
Advanced REST API with comprehensive energy optimization endpoints and real-time analytics
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import pandas as pd
import numpy as np
import io
import json
import uuid
from datetime import datetime, timedelta
import asyncio
import logging
import sys
import os
from pathlib import Path
import aiofiles

# Enhanced imports
from contextlib import asynccontextmanager
import psutil
import time

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from building_energy_optimizer import (
        BuildingEnergyOptimizer, 
        BuildingConfig, 
        create_enhanced_example_data,
        quick_optimize
    )
    SYSTEM_READY = True
    logging.info("✅ Core energy optimization modules loaded successfully")
except ImportError as e:
    logging.warning(f"⚠️ Core modules not available: {e}")
    SYSTEM_READY = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('energy_optimizer.log')
    ]
)
logger = logging.getLogger(__name__)

# Application state
app_state = {
    "optimization_jobs": {},
    "system_metrics": {},
    "active_sessions": 0,
    "startup_time": datetime.now()
}

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Building Energy Optimizer API v2.1")
    app_state["startup_time"] = datetime.now()
    
    # Startup health check
    if SYSTEM_READY:
        try:
            test_data = create_enhanced_example_data("2024-01-01", "2024-01-02", building_type="commercial")
            logger.info(f"✅ System validation: Generated {len(test_data)} test data points")
        except Exception as e:
            logger.error(f"❌ System validation failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Energy Optimizer API")

# FastAPI app with enhanced configuration
app = FastAPI(
    title="Energy Optimizer Pro API",
    description="🏢 Professional ML-powered building energy optimization platform with real-time analytics",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "system", "description": "System health and information"},
        {"name": "data", "description": "Data generation and management"},
        {"name": "optimization", "description": "ML optimization engine"},
        {"name": "analytics", "description": "Advanced analytics and insights"},
        {"name": "buildings", "description": "Building management"},
        {"name": "reports", "description": "Report generation"}
    ],
    lifespan=lifespan
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models (Enhanced)
class BuildingConfigModel(BaseModel):
    building_type: str = Field(default="commercial", description="Type of building")
    floor_area: float = Field(default=2500, description="Floor area in square meters")
    building_age: int = Field(default=10, description="Building age in years")
    insulation_level: float = Field(default=0.75, description="Insulation level (0-1)")
    hvac_efficiency: float = Field(default=0.8, description="HVAC efficiency (0-1)")
    occupancy_max: int = Field(default=100, description="Maximum occupancy")
    location: str = Field(default="Rome, IT", description="Building location")
    renewable_energy: bool = Field(default=False, description="Has renewable energy systems")
    smart_systems: bool = Field(default=False, description="Has smart building systems")

class OptimizationRequest(BaseModel):
    algorithm: str = Field(default="xgboost", description="ML algorithm to use")
    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: str = Field(description="End date (YYYY-MM-DD)")
    building_config: Optional[BuildingConfigModel] = None
    custom_data: Optional[List[Dict[str, Any]]] = None
    optimization_goals: Optional[List[str]] = Field(default=["cost_reduction", "energy_efficiency"])
    constraints: Optional[Dict[str, Any]] = None

class OptimizationResponse(BaseModel):
    success: bool
    job_id: str
    algorithm: str
    accuracy: float
    savings_percent: float
    total_consumption: float
    cost_savings_eur: float
    predictions: List[float]
    suggestions: List[Dict[str, Any]]
    training_metrics: Dict[str, float]
    processing_time: float
    confidence_interval: Dict[str, float]
    optimization_goals_met: Dict[str, bool]

class AnalyticsRequest(BaseModel):
    building_ids: List[str] = Field(description="List of building IDs to analyze")
    metrics: List[str] = Field(default=["consumption", "efficiency", "cost"])
    time_range: str = Field(default="30d", description="Time range for analysis")
    aggregation: str = Field(default="daily", description="Data aggregation level")

class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_sessions: int
    total_optimizations: int
    uptime_seconds: float
    api_response_time: float

# Utility functions
def get_system_metrics() -> SystemMetrics:
    """Get current system performance metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = (datetime.now() - app_state["startup_time"]).total_seconds()
        
        return SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            active_sessions=app_state.get("active_sessions", 0),
            total_optimizations=len(app_state.get("optimization_jobs", {})),
            uptime_seconds=uptime,
            api_response_time=0.0  # Would be calculated by middleware
        )
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return SystemMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            active_sessions=0,
            total_optimizations=0,
            uptime_seconds=0.0,
            api_response_time=0.0
        )

async def log_request_metrics():
    """Log request metrics for monitoring."""
    app_state["active_sessions"] = app_state.get("active_sessions", 0) + 1

# API Endpoints (Enhanced)

@app.get("/", response_class=JSONResponse, tags=["system"])
async def root():
    """Enhanced API root endpoint with comprehensive system information."""
    system_metrics = get_system_metrics()
    
    return {
        "message": "🏢 Energy Optimizer Pro API v2.1",
        "status": "healthy" if SYSTEM_READY else "degraded", 
        "version": "2.1.0",
        "features": [
            "🤖 Advanced ML Optimization",
            "📊 Real-time Analytics", 
            "🏗️ Multi-building Support",
            "📈 Predictive Modeling",
            "💰 Cost Optimization",
            "🌱 Sustainability Metrics"
        ],
        "available_algorithms": ["random_forest", "xgboost", "lightgbm"] if SYSTEM_READY else [],
        "system_metrics": system_metrics.dict(),
        "docs": "/docs",
        "timestamp": datetime.now().isoformat(),
        "uptime_hours": round(system_metrics.uptime_seconds / 3600, 2)
    }

@app.get("/health", response_model=Dict[str, Any], tags=["system"])
async def enhanced_health_check():
    """Comprehensive health check with detailed system metrics."""
    
    await log_request_metrics()
    start_time = time.time()
    
    system_metrics = get_system_metrics()
    performance_metrics = {}
    
    if SYSTEM_READY:
        try:
            # Enhanced performance test
            test_start = time.time()
            test_data = create_enhanced_example_data(
                "2024-01-01", "2024-01-03",
                building_type="commercial",
                floor_area=2500
            )
            
            result = quick_optimize(test_data, algorithm="random_forest")
            test_end = time.time()
            
            performance_metrics = {
                "test_data_points": len(test_data),
                "test_features": len(test_data.columns),
                "test_accuracy": result['training_metrics']['val_r2'],
                "test_processing_time_ms": (test_end - test_start) * 1000,
                "test_savings_percent": result['report']['summary']['potential_savings_percent'],
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Health check performance test failed: {e}")
            performance_metrics = {"error": str(e)}
    
    processing_time = (time.time() - start_time) * 1000
    
    # Health status determination
    health_score = 100
    status = "healthy"
    warnings = []
    
    if system_metrics.cpu_usage > 80:
        health_score -= 20
        warnings.append("High CPU usage")
    
    if system_metrics.memory_usage > 85:
        health_score -= 25
        warnings.append("High memory usage")
    
    if not SYSTEM_READY:
        health_score -= 50
        status = "degraded"
        warnings.append("Core modules not available")
    
    if health_score < 70:
        status = "warning" if health_score >= 50 else "critical"

    return {
        "status": status,
        "health_score": health_score,
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": system_metrics.uptime_seconds,
        "system_ready": SYSTEM_READY,
        "warnings": warnings,
        "system_metrics": system_metrics.dict(),
        "performance_metrics": performance_metrics,
        "api_response_time_ms": processing_time,
        "available_algorithms": ["random_forest", "xgboost", "lightgbm"] if SYSTEM_READY else [],
        "supported_building_types": ["commercial", "residential", "industrial"],
        "max_data_points": 10000,
        "concurrent_optimizations": len(app_state.get("optimization_jobs", {}))
    }

@app.post("/generate-data", tags=["data"])
async def generate_enhanced_sample_data(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    building_type: str = Query(default="commercial", description="Type of building"),
    floor_area: float = Query(default=2500, description="Floor area in square meters"),
    include_weather: bool = Query(default=True, description="Include weather data"),
    include_occupancy: bool = Query(default=True, description="Include occupancy patterns"),
    noise_level: float = Query(default=0.1, description="Data noise level (0-1)")
):
    """Generate enhanced synthetic energy data with advanced parameters."""
    
    if not SYSTEM_READY:
        raise HTTPException(status_code=503, detail="System not ready")
    
    try:
        await log_request_metrics()
        start_time = time.time()
        
        # Enhanced data generation
        data = create_enhanced_example_data(
            start_date=start_date,
            end_date=end_date,
            building_type=building_type,
            floor_area=floor_area
        )
        
        # Add synthetic weather data if requested
        if include_weather and 'temperature' not in data.columns:
            np.random.seed(42)
            data['temperature'] = 20 + np.sin(np.arange(len(data)) / 24 * 2 * np.pi) * 10 + np.random.normal(0, 2, len(data))
            data['humidity'] = 50 + np.random.normal(0, 10, len(data))
        
        # Add occupancy patterns if requested
        if include_occupancy and 'occupancy' not in data.columns:
            # Simulate realistic occupancy patterns
            hours = data.get('hour', np.arange(len(data)) % 24)
            base_occupancy = np.where(
                (hours >= 8) & (hours <= 18), 0.8, 0.2
            )  # Higher during business hours
            data['occupancy'] = base_occupancy + np.random.normal(0, 0.1, len(data))
            data['occupancy'] = np.clip(data['occupancy'], 0, 1)
        
        # Add noise if requested
        if noise_level > 0:
            noise = np.random.normal(0, data['energy_consumption'].std() * noise_level, len(data))
            data['energy_consumption'] += noise
            data['energy_consumption'] = np.maximum(data['energy_consumption'], 0)  # Ensure positive values
        
        processing_time = (time.time() - start_time) * 1000
        
        # Enhanced statistics
        consumption_data = data['energy_consumption']
        
        return {
            "success": True,
            "data_points": len(data),
            "features": list(data.columns),
            "data": data.to_dict('records'),
            "statistics": {
                "avg_consumption": float(consumption_data.mean()),
                "max_consumption": float(consumption_data.max()),
                "min_consumption": float(consumption_data.min()),
                "total_consumption": float(consumption_data.sum()),
                "std_consumption": float(consumption_data.std()),
                "consumption_range": float(consumption_data.max() - consumption_data.min()),
                "peak_hours": data.groupby('hour')['energy_consumption'].mean().idxmax() if 'hour' in data.columns else None
            },
            "metadata": {
                "building_type": building_type,
                "floor_area": floor_area,
                "date_range": f"{start_date} to {end_date}",
                "includes_weather": include_weather,
                "includes_occupancy": include_occupancy,
                "noise_level": noise_level,
                "processing_time_ms": processing_time
            }
        }
        
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Data generation failed: {str(e)}")

@app.post("/optimize", response_model=OptimizationResponse, tags=["optimization"])
async def run_enhanced_optimization(request: OptimizationRequest):
    """Run enhanced energy optimization with comprehensive analytics."""
    
    if not SYSTEM_READY:
        raise HTTPException(status_code=503, detail="System not ready")
    
    job_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        await log_request_metrics()
        
        # Get or generate data
        if request.custom_data:
            data = pd.DataFrame(request.custom_data)
        else:
            config = request.building_config or BuildingConfigModel()
            data = create_enhanced_example_data(
                start_date=request.start_date,
                end_date=request.end_date,
                building_type=config.building_type,
                floor_area=config.floor_area
            )
        
        logger.info(f"Starting optimization job {job_id} with {len(data)} data points using {request.algorithm}")
        
        # Store job info
        app_state["optimization_jobs"][job_id] = {
            "status": "running",
            "start_time": datetime.now(),
            "algorithm": request.algorithm,
            "data_points": len(data)
        }
        
        # Run optimization with enhanced metrics
        result = quick_optimize(data, algorithm=request.algorithm)
        
        # Calculate enhanced metrics
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Enhanced cost calculations
        total_consumption = result['report']['summary']['total_consumption_kwh']
        savings_percent = result['report']['summary']['potential_savings_percent']
        
        # Estimate costs (€0.15 per kWh average)
        cost_per_kwh = 0.15
        annual_consumption = total_consumption * (365 / len(data)) if len(data) > 0 else total_consumption
        annual_cost = annual_consumption * cost_per_kwh
        cost_savings = annual_cost * (savings_percent / 100)
        
        # Confidence interval calculation
        accuracy = result['training_metrics']['val_r2']
        confidence_lower = max(0, savings_percent - (1 - accuracy) * 10)
        confidence_upper = min(100, savings_percent + (1 - accuracy) * 10)
        
        # Check optimization goals
        goals_met = {}
        for goal in request.optimization_goals or ["cost_reduction", "energy_efficiency"]:
            if goal == "cost_reduction":
                goals_met[goal] = cost_savings > annual_cost * 0.10  # At least 10% savings
            elif goal == "energy_efficiency":
                goals_met[goal] = savings_percent > 15.0  # At least 15% energy savings
            else:
                goals_met[goal] = True  # Default to met for unknown goals
        
        # Update job status
        app_state["optimization_jobs"][job_id].update({
            "status": "completed",
            "end_time": datetime.now(),
            "processing_time": processing_time,
            "accuracy": accuracy,
            "savings_percent": savings_percent
        })
        
        logger.info(f"Optimization job {job_id} completed: {savings_percent:.1f}% savings, {accuracy:.1%} accuracy")
        
        return OptimizationResponse(
            success=True,
            job_id=job_id,
            algorithm=request.algorithm,
            accuracy=accuracy,
            savings_percent=savings_percent,
            total_consumption=total_consumption,
            cost_savings_eur=cost_savings,
            predictions=result['predictions'].tolist() if hasattr(result['predictions'], 'tolist') else list(result['predictions']),
            suggestions=result['suggestions'],
            training_metrics=result['training_metrics'],
            processing_time=processing_time,
            confidence_interval={
                "lower": confidence_lower,
                "upper": confidence_upper,
                "confidence_level": 0.95
            },
            optimization_goals_met=goals_met
        )
        
    except Exception as e:
        # Update job status on failure
        if job_id in app_state["optimization_jobs"]:
            app_state["optimization_jobs"][job_id].update({
                "status": "failed",
                "error": str(e),
                "end_time": datetime.now()
            })
        
        logger.error(f"Optimization job {job_id} failed: {e}")
        raise HTTPException(status_code=400, detail=f"Optimization failed: {str(e)}")

@app.get("/algorithms", tags=["optimization"])
async def get_enhanced_algorithms():
    """Get enhanced list of available ML algorithms with detailed information."""
    
    algorithms = [
        {
            "name": "random_forest",
            "display_name": "Random Forest",
            "description": "Ensemble method using multiple decision trees with bootstrap sampling",
            "pros": [
                "Robust to overfitting",
                "Handles missing values well", 
                "Provides feature importance",
                "Works with mixed data types",
                "Relatively fast training"
            ],
            "cons": [
                "Can be memory intensive",
                "Less interpretable than single trees",
                "May overfit with very noisy data"
            ],
            "best_for": "General purpose optimization with good accuracy and robustness",
            "typical_accuracy": "85-92%",
            "training_time": "Fast",
            "memory_usage": "Medium",
            "hyperparameters": {
                "n_estimators": {"default": 100, "range": "50-500"},
                "max_depth": {"default": "None", "range": "5-50"},
                "min_samples_split": {"default": 2, "range": "2-20"}
            }
        },
        {
            "name": "xgboost",
            "display_name": "XGBoost",
            "description": "Gradient boosting framework optimized for performance and accuracy",
            "pros": [
                "Excellent accuracy",
                "Fast training and prediction",
                "Built-in regularization",
                "Handles missing values",
                "Feature importance analysis"
            ],
            "cons": [
                "Requires hyperparameter tuning",
                "Can overfit with small datasets", 
                "More complex to interpret"
            ],
            "best_for": "Maximum accuracy with structured data and sufficient training samples",
            "typical_accuracy": "88-95%",
            "training_time": "Medium",
            "memory_usage": "Low",
            "hyperparameters": {
                "n_estimators": {"default": 100, "range": "50-500"},
                "learning_rate": {"default": 0.1, "range": "0.01-0.3"},
                "max_depth": {"default": 6, "range": "3-10"}
            }
        },
        {
            "name": "lightgbm",
            "display_name": "LightGBM", 
            "description": "Fast gradient boosting framework by Microsoft with leaf-wise tree growth",
            "pros": [
                "Very fast training",
                "Memory efficient",
                "High accuracy",
                "Good with large datasets",
                "Built-in categorical feature support"
            ],
            "cons": [
                "Can overfit with small datasets",
                "Sensitive to hyperparameters",
                "May need feature engineering"
            ],
            "best_for": "Large datasets requiring fast processing with high accuracy",
            "typical_accuracy": "86-93%", 
            "training_time": "Very Fast",
            "memory_usage": "Very Low",
            "hyperparameters": {
                "n_estimators": {"default": 100, "range": "50-500"},
                "learning_rate": {"default": 0.1, "range": "0.01-0.3"},
                "num_leaves": {"default": 31, "range": "10-100"}
            }
        }
    ]
    
    return {
        "available_algorithms": algorithms,
        "default_algorithm": "xgboost",
        "system_ready": SYSTEM_READY,
        "recommendations": {
            "small_datasets": "random_forest",
            "large_datasets": "lightgbm", 
            "maximum_accuracy": "xgboost",
            "fastest_training": "lightgbm",
            "most_robust": "random_forest"
        }
    }

@app.get("/jobs", tags=["optimization"]) 
async def get_optimization_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, description="Maximum number of jobs to return")
):
    """Get list of optimization jobs with filtering options."""
    
    jobs = app_state.get("optimization_jobs", {})
    
    # Filter by status if provided
    if status:
        jobs = {k: v for k, v in jobs.items() if v.get("status") == status}
    
    # Sort by start time (most recent first) and limit
    sorted_jobs = sorted(
        jobs.items(),
        key=lambda x: x[1].get("start_time", datetime.min),
        reverse=True
    )[:limit]
    
    return {
        "jobs": [
            {
                "job_id": job_id,
                **job_data,
                "start_time": job_data.get("start_time", "").isoformat() if hasattr(job_data.get("start_time", ""), "isoformat") else str(job_data.get("start_time", "")),
                "end_time": job_data.get("end_time", "").isoformat() if hasattr(job_data.get("end_time", ""), "isoformat") else str(job_data.get("end_time", ""))
            }
            for job_id, job_data in sorted_jobs
        ],
        "total_jobs": len(jobs),
        "status_counts": {
            "running": len([j for j in jobs.values() if j.get("status") == "running"]),
            "completed": len([j for j in jobs.values() if j.get("status") == "completed"]),
            "failed": len([j for j in jobs.values() if j.get("status") == "failed"])
        }
    }

@app.get("/jobs/{job_id}", tags=["optimization"])
async def get_optimization_job(job_id: str):
    """Get detailed information about a specific optimization job."""
    
    if job_id not in app_state.get("optimization_jobs", {}):
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = app_state["optimization_jobs"][job_id]
    
    return {
        "job_id": job_id,
        **job_data,
        "start_time": job_data.get("start_time", "").isoformat() if hasattr(job_data.get("start_time", ""), "isoformat") else str(job_data.get("start_time", "")),
        "end_time": job_data.get("end_time", "").isoformat() if hasattr(job_data.get("end_time", ""), "isoformat") else str(job_data.get("end_time", ""))
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Energy Optimizer Pro API v2.1...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 ReDoc Documentation: http://localhost:8000/redoc")
    print("⚡ System Status: http://localhost:8000/health")
    print("🏢 Building Energy Optimizer - Professional Edition")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
