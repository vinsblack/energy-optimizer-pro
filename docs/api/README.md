# Building Energy Optimizer API Documentation v2.0

## Overview

The Building Energy Optimizer provides a comprehensive REST API for energy optimization, analytics, and building management. The API is built with FastAPI and includes automatic documentation, request validation, and comprehensive error handling.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API supports multiple authentication methods:

### 1. API Key Authentication
```http
Authorization: Bearer eo_your_api_key_here
```

### 2. JWT Token Authentication  
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Rate Limiting

- **General endpoints**: 200 requests/hour per IP
- **Prediction endpoints**: 100 requests/hour per IP  
- **Optimization endpoints**: 10 requests/hour per IP

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## API Endpoints

### Health and Status

#### GET `/`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "available_algorithms": ["xgboost", "lightgbm", "random_forest"],
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600
}
```

#### GET `/health`
Detailed health status.

**Response:**
```json
{
  "overall_status": "healthy",
  "status_counts": {
    "healthy": 5,
    "warning": 1, 
    "critical": 0,
    "unknown": 0
  },
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection OK",
      "response_time_ms": 45.2
    },
    "ml_models": {
      "status": "healthy", 
      "message": "ML system operational",
      "response_time_ms": 12.8
    }
  }
}
```

### Energy Optimization

#### POST `/optimize`
Run complete energy optimization analysis.

**Request Body:**
```json
{
  "algorithm": "xgboost",
  "building_config": {
    "building_type": "commercial",
    "floor_area": 2500,
    "building_age": 8,
    "insulation_level": 0.75,
    "hvac_efficiency": 0.85,
    "occupancy_max": 150,
    "renewable_energy": true
  },
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response:**
```json
{
  "success": true,
  "optimization_id": "opt_20240115_103045_abc123",
  "predictions": [85.2, 92.1, 78.5, ...],
  "suggestions": [
    {
      "timestamp": "2024-01-01T10:00:00Z",
      "current_consumption": 120.5,
      "potential_savings": 18.3,
      "priority": "high",
      "suggestions": [
        {
          "category": "HVAC",
          "type": "temperature_adjustment",
          "action": "Reduce heating setpoint by 2°C during peak hours",
          "estimated_savings_kwh": 15.2,
          "estimated_savings_percent": 12.6,
          "implementation_difficulty": "Easy"
        }
      ]
    }
  ],
  "report": {
    "summary": {
      "total_consumption_kwh": 2450.8,
      "average_hourly_consumption_kwh": 102.1,
      "peak_consumption_kwh": 145.3,
      "total_potential_savings_kwh": 367.6,
      "potential_savings_percent": 15.0,
      "cost_savings_estimate_eur": 44.11
    },
    "time_analysis": {
      "peak_hours": [9, 10, 17, 18],
      "low_consumption_hours": [1, 2, 3, 4],
      "weekend_vs_weekday_ratio": 0.72
    },
    "suggestions_by_category": {
      "HVAC": 12,
      "Lighting": 5,
      "Equipment": 3,
      "Renewable": 2
    }
  },
  "training_metrics": {
    "val_r2": 0.876,
    "val_mae": 8.32,
    "training_samples": 744,
    "features_count": 28
  },
  "model_info": {
    "algorithm": "xgboost",
    "feature_importance_top_5": {
      "temperature": 0.324,
      "occupancy": 0.198,
      "hour": 0.156,
      "solar_radiation": 0.134,
      "day_of_week": 0.089
    }
  }
}
```

#### POST `/predict`
Single-point energy consumption prediction.

**Request Body:**
```json
{
  "temperature": 22.5,
  "humidity": 55.0,
  "solar_radiation": 650.0,
  "wind_speed": 3.2,
  "precipitation": 0.0,
  "occupancy": 0.7,
  "hour": 14,
  "day_of_week": 2,
  "month": 6
}
```

**Response:**
```json
{
  "success": true,
  "predicted_consumption": 95.7,
  "confidence_interval": [89.2, 102.1],
  "factors": {
    "temperature_impact": "moderate_increase",
    "occupancy_impact": "high_increase", 
    "time_impact": "peak_hours"
  },
  "optimization_suggestions": [
    "Consider reducing HVAC load during peak occupancy",
    "Schedule non-critical equipment for off-peak hours"
  ]
}
```

### Data Management

#### POST `/upload-data`
Upload energy consumption data for analysis.

**Request:**
```http
POST /upload-data
Content-Type: multipart/form-data

file: energy_data.csv
algorithm: xgboost
building_type: commercial
```

**CSV Format:**
```csv
timestamp,energy_consumption,temperature,humidity,occupancy
2024-01-01T00:00:00Z,85.2,18.5,65.0,0.1
2024-01-01T01:00:00Z,82.1,18.2,66.0,0.05
...
```

**Response:**
```json
{
  "success": true,
  "file_info": {
    "filename": "energy_data.csv",
    "size_bytes": 15840,
    "records_count": 168
  },
  "data_validation": {
    "valid_records": 168,
    "invalid_records": 0,
    "missing_values": 0,
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-07T23:00:00Z"
    }
  },
  "optimization_results": {
    "potential_savings_percent": 12.5,
    "cost_savings_eur": 89.40,
    "suggestions_count": 18
  }
}
```

#### GET `/buildings`
List all buildings in the system.

**Query Parameters:**
- `limit` (optional): Maximum number of results (default: 50)
- `offset` (optional): Number of results to skip (default: 0)
- `building_type` (optional): Filter by building type

**Response:**
```json
{
  "success": true,
  "buildings": [
    {
      "id": 1,
      "name": "Main Office Building",
      "building_type": "commercial",
      "floor_area": 2500,
      "building_age": 8,
      "renewable_energy": true,
      "last_optimization": "2024-01-15T09:30:00Z",
      "avg_consumption_kwh": 102.5,
      "efficiency_rating": "Good"
    }
  ],
  "total_count": 1,
  "page_info": {
    "limit": 50,
    "offset": 0,
    "has_next": false
  }
}
```

#### POST `/buildings`
Create a new building.

**Request Body:**
```json
{
  "name": "New Office Building",
  "building_type": "commercial",
  "floor_area": 3000,
  "building_age": 5,
  "insulation_level": 0.8,
  "hvac_efficiency": 0.9,
  "occupancy_max": 200,
  "renewable_energy": true,
  "latitude": 41.9028,
  "longitude": 12.4964
}
```

**Response:**
```json
{
  "success": true,
  "building": {
    "id": 2,
    "name": "New Office Building",
    "building_type": "commercial",
    "floor_area": 3000,
    "created_at": "2024-01-15T10:45:00Z",
    "efficiency_score": 78.5
  }
}
```

### Model Management

#### GET `/models`
List all trained models.

**Response:**
```json
{
  "success": true,
  "trained_models": [
    {
      "optimizer_id": "opt_20240115_103045",
      "algorithm": "xgboost",
      "building_type": "commercial",
      "training_date": "2024-01-15T10:30:45Z",
      "performance_metrics": {
        "r2_score": 0.876,
        "mae": 8.32
      },
      "training_samples": 744
    }
  ],
  "total_models": 1,
  "algorithms_available": ["xgboost", "lightgbm", "random_forest"]
}
```

#### GET `/feature-importance/{optimizer_id}`
Get feature importance for a trained model.

**Response:**
```json
{
  "success": true,
  "optimizer_id": "opt_20240115_103045",
  "feature_importance": {
    "temperature": 0.324,
    "occupancy": 0.198,
    "hour": 0.156,
    "solar_radiation": 0.134,
    "day_of_week": 0.089,
    "humidity": 0.067,
    "wind_speed": 0.032
  },
  "top_10_features": [
    {"feature": "temperature", "importance": 0.324},
    {"feature": "occupancy", "importance": 0.198},
    {"feature": "hour", "importance": 0.156}
  ]
}
```

### Analytics and Reporting

#### POST `/analytics/advanced`
Run advanced analytics on energy data.

**Request Body:**
```json
{
  "energy_data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "energy_consumption": 85.2,
      "temperature": 18.5,
      "humidity": 65.0,
      "occupancy": 0.1
    }
  ],
  "building_config": {
    "building_type": "commercial",
    "floor_area": 2500
  },
  "analysis_type": "complete"
}
```

**Response:**
```json
{
  "success": true,
  "analysis_results": {
    "statistical_summary": {
      "descriptive_stats": {
        "mean": 95.4,
        "median": 92.1,
        "std": 18.7,
        "skewness": 0.23,
        "kurtosis": -0.45
      }
    },
    "consumption_patterns": {
      "peak_hours": [9, 10, 17, 18],
      "weekday_avg": 102.3,
      "weekend_avg": 73.8
    },
    "anomaly_detection": {
      "statistical_anomalies": {
        "count": 5,
        "percentage": 2.98
      }
    },
    "efficiency_metrics": {
      "energy_intensity_kwh_m2_year": 156.8,
      "efficiency_rating": "Good",
      "efficiency_score": 78.2
    }
  }
}
```

#### GET `/reports/{building_id}`
Generate comprehensive energy report for a building.

**Query Parameters:**
- `start_date`: Analysis start date (YYYY-MM-DD)
- `end_date`: Analysis end date (YYYY-MM-DD)
- `format`: Report format (json, html, pdf)

**Response:**
```json
{
  "success": true,
  "report": {
    "building_info": {
      "id": 1,
      "name": "Main Office Building",
      "building_type": "commercial"
    },
    "analysis_period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "total_days": 31
    },
    "energy_summary": {
      "total_consumption_kwh": 3187.5,
      "daily_average_kwh": 102.8,
      "peak_demand_kw": 145.3,
      "load_factor": 0.71
    },
    "optimization_opportunities": {
      "total_potential_savings_kwh": 478.1,
      "potential_savings_percent": 15.0,
      "estimated_cost_savings_eur": 573.72,
      "payback_period_months": 18
    },
    "recommendations": [
      {
        "category": "HVAC",
        "priority": "High",
        "action": "Install smart thermostats",
        "estimated_savings": "8-12%",
        "implementation_cost": "€5,000-€8,000"
      }
    ]
  },
  "generated_at": "2024-01-15T10:45:00Z"
}
```

### Plugin Management

#### GET `/plugins`
List all available plugins.

**Response:**
```json
{
  "success": true,
  "plugins": {
    "simulated_iot": {
      "name": "Simulated IoT Devices",
      "version": "1.0.0",
      "category": "iot",
      "enabled": true,
      "loaded": true,
      "description": "Simulated IoT devices for testing"
    },
    "email_notifications": {
      "name": "Email Notifications",
      "version": "1.0.0", 
      "category": "notification",
      "enabled": true,
      "loaded": true
    }
  },
  "plugin_summary": {
    "total_plugins": 5,
    "loaded_plugins": 4,
    "enabled_plugins": 4
  }
}
```

#### POST `/plugins/{plugin_name}/execute`
Execute a specific plugin.

**Request Body:**
```json
{
  "action": "collect_data",
  "parameters": {
    "device_count": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "plugin_name": "simulated_iot",
  "execution_time_ms": 156.7,
  "result": {
    "iot_data": [
      {
        "timestamp": "2024-01-15T10:45:00Z",
        "device_id": "sim_device_001",
        "sensor_type": "energy_consumption",
        "value": 87.5,
        "unit": "kWh"
      }
    ],
    "devices_online": 10,
    "total_devices": 10
  }
}
```

### Weather Integration

#### GET `/weather/current`
Get current weather data.

**Query Parameters:**
- `lat`: Latitude (default: 41.9028)
- `lon`: Longitude (default: 12.4964)

**Response:**
```json
{
  "success": true,
  "weather": {
    "temperature": 22.5,
    "humidity": 58.0,
    "solar_radiation": 750.0,
    "wind_speed": 4.2,
    "precipitation": 0.0,
    "pressure": 1013.25,
    "conditions": "clear_sky"
  },
  "location": {
    "latitude": 41.9028,
    "longitude": 12.4964,
    "city": "Rome",
    "country": "IT"
  },
  "data_source": "OpenWeatherMap",
  "timestamp": "2024-01-15T10:45:00Z"
}
```

#### GET `/weather/forecast`
Get weather forecast.

**Query Parameters:**
- `lat`: Latitude
- `lon`: Longitude  
- `hours`: Forecast hours (default: 24, max: 120)

**Response:**
```json
{
  "success": true,
  "forecast": [
    {
      "timestamp": "2024-01-15T11:00:00Z",
      "temperature": 23.1,
      "humidity": 56.0,
      "solar_radiation": 780.0,
      "conditions": "clear_sky"
    }
  ],
  "forecast_hours": 24,
  "location": {
    "latitude": 41.9028,
    "longitude": 12.4964
  }
}
```

## Error Handling

All API endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "type": "validation_error",
    "message": "Invalid building_type. Must be one of: residential, commercial, industrial",
    "details": {
      "field": "building_config.building_type",
      "received_value": "invalid_type",
      "allowed_values": ["residential", "commercial", "industrial"]
    }
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "type": "authentication_error",
    "message": "Invalid or missing authentication token"
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 300 seconds.",
    "details": {
      "limit": 10,
      "window": "1 hour",
      "retry_after": 300
    }
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "type": "internal_error",
    "message": "An internal error occurred while processing your request",
    "error_id": "err_20240115_104500_xyz789"
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

## Code Examples

### Python Client Example
```python
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "eo_your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Run optimization
optimization_request = {
    "algorithm": "xgboost",
    "building_config": {
        "building_type": "commercial",
        "floor_area": 2500,
        "building_age": 8,
        "insulation_level": 0.75,
        "hvac_efficiency": 0.85,
        "occupancy_max": 150,
        "renewable_energy": True
    },
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
}

response = requests.post(
    f"{API_BASE_URL}/optimize",
    headers=headers,
    json=optimization_request
)

if response.status_code == 200:
    result = response.json()
    savings_percent = result['report']['summary']['potential_savings_percent']
    print(f"Potential savings: {savings_percent:.1f}%")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript Client Example
```javascript
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'eo_your_api_key_here';

const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

// Single prediction
async function predictConsumption(sensorData) {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(sensorData)
    });
    
    if (response.ok) {
        const result = await response.json();
        return result.predicted_consumption;
    } else {
        throw new Error(`API Error: ${response.status}`);
    }
}

// Usage
const sensorData = {
    temperature: 22.5,
    humidity: 55.0,
    solar_radiation: 650.0,
    wind_speed: 3.2,
    precipitation: 0.0,
    occupancy: 0.7,
    hour: 14,
    day_of_week: 2,
    month: 6
};

predictConsumption(sensorData)
    .then(consumption => console.log(`Predicted: ${consumption} kWh`))
    .catch(error => console.error('Error:', error));
```

### cURL Examples

#### Health Check
```bash
curl -X GET "http://localhost:8000/" \
  -H "Authorization: Bearer eo_your_api_key_here"
```

#### Run Optimization
```bash
curl -X POST "http://localhost:8000/optimize" \
  -H "Authorization: Bearer eo_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "xgboost",
    "building_config": {
      "building_type": "commercial",
      "floor_area": 2500,
      "building_age": 8,
      "renewable_energy": true
    },
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }'
```

#### Upload Data
```bash
curl -X POST "http://localhost:8000/upload-data" \
  -H "Authorization: Bearer eo_your_api_key_here" \
  -F "file=@energy_data.csv" \
  -F "algorithm=xgboost" \
  -F "building_type=commercial"
```

## WebSocket Support

### Real-time Optimization Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/optimization');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'optimization_progress') {
        console.log(`Progress: ${data.progress}%`);
    } else if (data.type === 'optimization_complete') {
        console.log('Optimization completed!', data.result);
    }
};

// Start optimization via WebSocket
ws.send(JSON.stringify({
    action: 'start_optimization',
    config: {
        algorithm: 'xgboost',
        building_config: {...}
    }
}));
```

## SDK Libraries

### Python SDK
```bash
pip install building-energy-optimizer-sdk
```

```python
from beo_sdk import EnergyOptimizerClient

client = EnergyOptimizerClient(
    base_url="http://localhost:8000",
    api_key="eo_your_api_key_here"
)

# Run optimization
result = client.optimize_building(
    algorithm="xgboost",
    building_config={
        "building_type": "commercial",
        "floor_area": 2500
    },
    date_range=("2024-01-01", "2024-01-31")
)

print(f"Potential savings: {result.savings_percent:.1f}%")
```

### Node.js SDK
```bash
npm install building-energy-optimizer-sdk
```

```javascript
const { EnergyOptimizerClient } = require('building-energy-optimizer-sdk');

const client = new EnergyOptimizerClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'eo_your_api_key_here'
});

// Run optimization
const result = await client.optimizeBuilding({
    algorithm: 'xgboost',
    buildingConfig: {
        buildingType: 'commercial',
        floorArea: 2500
    },
    dateRange: ['2024-01-01', '2024-01-31']
});

console.log(`Potential savings: ${result.savingsPercent}%`);
```

## Best Practices

### 1. Authentication
- Store API keys securely (environment variables, secret managers)
- Rotate API keys regularly
- Use JWT tokens for web applications
- Implement proper session management

### 2. Rate Limiting
- Implement client-side rate limiting
- Cache responses when appropriate
- Use batch endpoints for multiple operations
- Monitor rate limit headers

### 3. Error Handling
- Always check response status codes
- Implement exponential backoff for retries
- Log errors with sufficient context
- Handle network timeouts gracefully

### 4. Data Management
- Validate data before uploading
- Use appropriate date formats (ISO 8601)
- Compress large datasets before upload
- Implement data pagination for large results

### 5. Performance
- Use appropriate algorithms for your use case
- Limit data ranges for large analyses
- Implement caching for repeated requests
- Monitor API response times

## Interactive Documentation

Visit the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- Explore all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

## Support

For API support and questions:
- 📧 Email: api-support@energy-optimizer.com
- 📚 Documentation: https://docs.energy-optimizer.com
- 🐛 Issues: https://github.com/your-username/building-energy-optimizer/issues
- 💬 Community: https://discord.gg/energy-optimizer
