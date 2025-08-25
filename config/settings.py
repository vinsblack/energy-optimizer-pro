"""
Configuration management for Building Energy Optimizer.
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from functools import lru_cache

class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    url: str = Field(
        default="sqlite:///building_energy.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Enable SQLAlchemy query logging"
    )
    pool_size: int = Field(
        default=5,
        env="DATABASE_POOL_SIZE",
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=10,
        env="DATABASE_MAX_OVERFLOW",
        description="Database connection pool overflow"
    )

class APIConfig(BaseSettings):
    """API configuration."""
    
    host: str = Field(
        default="0.0.0.0",
        env="API_HOST",
        description="API host address"
    )
    port: int = Field(
        default=8000,
        env="API_PORT",
        description="API port number"
    )
    reload: bool = Field(
        default=False,
        env="API_RELOAD",
        description="Enable auto-reload in development"
    )
    workers: int = Field(
        default=1,
        env="API_WORKERS",
        description="Number of worker processes"
    )
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )

class WeatherConfig(BaseSettings):
    """Weather API configuration."""
    
    openweathermap_api_key: Optional[str] = Field(
        default=None,
        env="OPENWEATHERMAP_API_KEY",
        description="OpenWeatherMap API key"
    )
    weather_cache_ttl: int = Field(
        default=3600,  # 1 hour
        env="WEATHER_CACHE_TTL",
        description="Weather data cache TTL in seconds"
    )
    default_location_lat: float = Field(
        default=41.9028,  # Rome
        env="DEFAULT_LAT",
        description="Default latitude for weather data"
    )
    default_location_lon: float = Field(
        default=12.4964,  # Rome
        env="DEFAULT_LON",
        description="Default longitude for weather data"
    )

class MLConfig(BaseSettings):
    """Machine Learning configuration."""
    
    default_algorithm: str = Field(
        default="xgboost",
        env="ML_DEFAULT_ALGORITHM",
        description="Default ML algorithm"
    )
    model_cache_dir: str = Field(
        default="models/",
        env="MODEL_CACHE_DIR",
        description="Directory to store trained models"
    )
    max_training_samples: int = Field(
        default=100000,
        env="ML_MAX_TRAINING_SAMPLES",
        description="Maximum number of samples for training"
    )
    validation_split: float = Field(
        default=0.2,
        env="ML_VALIDATION_SPLIT",
        description="Validation data split ratio"
    )
    feature_selection_threshold: float = Field(
        default=0.01,
        env="ML_FEATURE_THRESHOLD",
        description="Minimum feature importance threshold"
    )

class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format"
    )
    file_enabled: bool = Field(
        default=True,
        env="LOG_FILE_ENABLED",
        description="Enable file logging"
    )
    file_path: str = Field(
        default="logs/energy_optimizer.log",
        env="LOG_FILE_PATH",
        description="Log file path"
    )
    max_file_size: int = Field(
        default=10485760,  # 10MB
        env="LOG_MAX_FILE_SIZE",
        description="Maximum log file size in bytes"
    )
    backup_count: int = Field(
        default=5,
        env="LOG_BACKUP_COUNT",
        description="Number of log backup files to keep"
    )

class CacheConfig(BaseSettings):
    """Cache configuration."""
    
    redis_url: Optional[str] = Field(
        default=None,
        env="REDIS_URL",
        description="Redis connection URL"
    )
    default_ttl: int = Field(
        default=3600,  # 1 hour
        env="CACHE_DEFAULT_TTL",
        description="Default cache TTL in seconds"
    )
    enabled: bool = Field(
        default=True,
        env="CACHE_ENABLED",
        description="Enable caching"
    )

class AppConfig(BaseSettings):
    """Main application configuration."""
    
    # Environment
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY",
        description="Secret key for sessions and security"
    )
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    api: APIConfig = APIConfig()
    weather: WeatherConfig = WeatherConfig()
    ml: MLConfig = MLConfig()
    logging: LoggingConfig = LoggingConfig()
    cache: CacheConfig = CacheConfig()
    
    # Application-specific
    max_buildings_per_user: int = Field(
        default=10,
        env="MAX_BUILDINGS_PER_USER",
        description="Maximum buildings per user"
    )
    max_optimization_history: int = Field(
        default=100,
        env="MAX_OPTIMIZATION_HISTORY",
        description="Maximum optimization results to keep"
    )
    energy_cost_per_kwh: float = Field(
        default=0.12,  # €0.12 per kWh
        env="ENERGY_COST_PER_KWH",
        description="Energy cost per kWh in EUR"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()

def get_database_url() -> str:
    """Get database URL from configuration."""
    return get_config().database.url

def get_ml_config() -> MLConfig:
    """Get ML configuration."""
    return get_config().ml

def get_weather_config() -> WeatherConfig:
    """Get weather configuration."""
    return get_config().weather

def is_production() -> bool:
    """Check if running in production environment."""
    return get_config().environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment."""
    return get_config().environment.lower() == "development"

# Export commonly used configurations
config = get_config()

if __name__ == "__main__":
    # Print current configuration
    config = get_config()
    
    print("🔧 Building Energy Optimizer Configuration")
    print("=" * 50)
    print(f"Environment: {config.environment}")
    print(f"Debug Mode: {config.debug}")
    print(f"Database URL: {config.database.url}")
    print(f"API Host: {config.api.host}:{config.api.port}")
    print(f"Default Algorithm: {config.ml.default_algorithm}")
    print(f"Weather API Key: {'***' if config.weather.openweathermap_api_key else 'Not set'}")
    print(f"Log Level: {config.logging.level}")
    print(f"Cache Enabled: {config.cache.enabled}")
