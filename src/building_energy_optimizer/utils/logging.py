"""
Advanced logging configuration for Building Energy Optimizer.
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class ColoredFormatter(logging.Formatter):
    """Colored console log formatter."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'building_id'):
            log_entry['building_id'] = record.building_id
        if hasattr(record, 'optimization_id'):
            log_entry['optimization_id'] = record.optimization_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

class OptimizationLogger:
    """Specialized logger for optimization operations."""
    
    def __init__(self, name: str = "energy_optimizer"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate handlers."""
        # Don't setup if already configured
        if self.logger.handlers:
            return
        
        self.logger.setLevel(logging.INFO)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler with JSON format
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "energy_optimizer.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        
        error_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s\n'
            'File: %(pathname)s:%(lineno)d | Function: %(funcName)s\n'
            '%(exc_text)s\n' + '-'*80
        )
        error_handler.setFormatter(error_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def log_optimization_start(self, algorithm: str, building_id: Optional[int] = None, 
                             samples: Optional[int] = None):
        """Log optimization start."""
        extra = {}
        if building_id:
            extra['building_id'] = building_id
        
        message = f"Starting optimization with {algorithm}"
        if samples:
            message += f" on {samples} samples"
        
        self.logger.info(message, extra=extra)
    
    def log_optimization_complete(self, algorithm: str, execution_time: float,
                                r2_score: float, building_id: Optional[int] = None):
        """Log optimization completion."""
        extra = {
            'execution_time': execution_time,
            'r2_score': r2_score
        }
        if building_id:
            extra['building_id'] = building_id
        
        self.logger.info(
            f"Optimization complete: {algorithm} | R²: {r2_score:.3f} | Time: {execution_time:.2f}s",
            extra=extra
        )
    
    def log_prediction_batch(self, count: int, avg_consumption: float,
                           suggestions_generated: int):
        """Log batch prediction results."""
        self.logger.info(
            f"Batch prediction: {count} samples | Avg: {avg_consumption:.2f} kWh | "
            f"Suggestions: {suggestions_generated}"
        )
    
    def log_data_processing(self, original_samples: int, processed_samples: int,
                          features_count: int):
        """Log data processing results."""
        self.logger.info(
            f"Data processing: {original_samples} → {processed_samples} samples | "
            f"Features: {features_count}"
        )
    
    def log_api_request(self, endpoint: str, method: str, response_time: float,
                       status_code: int, user_id: Optional[str] = None):
        """Log API request."""
        extra = {
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code
        }
        if user_id:
            extra['user_id'] = user_id
        
        level = logging.INFO if status_code < 400 else logging.ERROR
        self.logger.log(
            level,
            f"API {method} {endpoint} | {status_code} | {response_time:.3f}s",
            extra=extra
        )
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """Log error with context."""
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} | {message}"
        
        self.logger.error(message, exc_info=True)

# Global logger instance
optimizer_logger = OptimizationLogger()

# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message."""
    optimizer_logger.logger.info(message, extra=kwargs)

def log_error(message: str, error: Optional[Exception] = None, **kwargs):
    """Log error message."""
    if error:
        optimizer_logger.logger.error(f"{message}: {str(error)}", exc_info=True, extra=kwargs)
    else:
        optimizer_logger.logger.error(message, extra=kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message."""
    optimizer_logger.logger.warning(message, extra=kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message."""
    optimizer_logger.logger.debug(message, extra=kwargs)

# Performance monitoring decorator
def log_performance(func):
    """Decorator to log function performance."""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            log_debug(f"Starting {function_name}")
            result = func(*args, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            log_info(f"Completed {function_name}", execution_time=execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            log_error(f"Failed {function_name}", error=e, execution_time=execution_time)
            raise
    
    return wrapper

if __name__ == "__main__":
    # Test logging system
    print("🧪 Testing logging system...")
    
    log_info("This is an info message")
    log_warning("This is a warning message")
    log_debug("This is a debug message")
    
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        log_error("Test error occurred", error=e)
    
    print("✅ Logging test complete. Check logs/ directory for output files.")
