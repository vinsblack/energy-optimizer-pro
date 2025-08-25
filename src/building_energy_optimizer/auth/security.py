"""
Authentication and security system for Building Energy Optimizer.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
import hashlib
from functools import wraps
import time
import logging
import os

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should come from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    buildings_quota: int = 10
    api_calls_quota: int = 1000

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    scopes: List[str] = []

class APIKey(BaseModel):
    id: str
    name: str
    key_hash: str
    user_id: int
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: int = 100  # requests per hour

# Rate limiting storage
rate_limit_storage: Dict[str, Dict] = {}

class SecurityManager:
    """Main security management class."""
    
    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key
        self.algorithm = ALGORITHM
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def generate_api_key(self, user_id: int, name: str) -> tuple:
        """Generate API key for user."""
        # Generate random API key
        api_key = f"eo_{secrets.token_urlsafe(32)}"
        
        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        return api_key, key_hash
    
    def verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        """Verify API key against stored hash."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return secrets.compare_digest(key_hash, stored_hash)

# Rate limiting
class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old entries
        if identifier in rate_limit_storage:
            rate_limit_storage[identifier] = [
                timestamp for timestamp in rate_limit_storage[identifier] 
                if timestamp > window_start
            ]
        else:
            rate_limit_storage[identifier] = []
        
        # Check current count
        current_count = len(rate_limit_storage[identifier])
        
        if current_count >= self.max_requests:
            return False
        
        # Add current request
        rate_limit_storage[identifier].append(now)
        return True
    
    def get_reset_time(self, identifier: str) -> int:
        """Get time until rate limit resets."""
        if identifier not in rate_limit_storage or not rate_limit_storage[identifier]:
            return 0
        
        oldest_request = min(rate_limit_storage[identifier])
        reset_time = oldest_request + self.window_seconds
        return max(0, int(reset_time - time.time()))

# Authentication dependencies
security_manager = SecurityManager()
rate_limiter = RateLimiter()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    
    try:
        payload = security_manager.verify_token(token)
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # In production, fetch user from database
        # For demo, return mock user
        user = User(
            id=int(user_id),
            username=username,
            email=f"{username}@example.com",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            buildings_quota=10,
            api_calls_quota=1000
        )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, 
            detail="The user doesn't have enough privileges"
        )
    return current_user

def require_auth(func):
    """Decorator to require authentication."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current_user from kwargs if present
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return await func(*args, **kwargs)
    return wrapper

def check_rate_limit(identifier: str, max_requests: int = 100):
    """Check rate limit for identifier."""
    limiter = RateLimiter(max_requests=max_requests)
    
    if not limiter.is_allowed(identifier):
        reset_time = limiter.get_reset_time(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
            headers={"Retry-After": str(reset_time)}
        )

async def rate_limit_middleware(request: Request):
    """Rate limiting middleware."""
    # Get client IP
    client_ip = request.client.host
    
    # Different limits for different endpoints
    endpoint = request.url.path
    
    if endpoint.startswith("/optimize"):
        max_requests = 10  # Lower limit for expensive operations
    elif endpoint.startswith("/predict"):
        max_requests = 100  # Higher limit for simple predictions
    else:
        max_requests = 200  # General endpoints
    
    check_rate_limit(client_ip, max_requests)

# Input validation and sanitization
class InputValidator:
    """Input validation and sanitization."""
    
    @staticmethod
    def validate_building_config(config: Dict) -> Dict:
        """Validate building configuration."""
        validated = {}
        
        # Building type
        valid_types = ['residential', 'commercial', 'industrial']
        building_type = config.get('building_type', 'commercial')
        if building_type not in valid_types:
            raise ValueError(f"Invalid building type. Must be one of: {valid_types}")
        validated['building_type'] = building_type
        
        # Floor area
        floor_area = float(config.get('floor_area', 1000))
        if not 10 <= floor_area <= 1000000:  # 10m² to 1,000,000m²
            raise ValueError("Floor area must be between 10 and 1,000,000 m²")
        validated['floor_area'] = floor_area
        
        # Building age
        building_age = int(config.get('building_age', 10))
        if not 0 <= building_age <= 200:
            raise ValueError("Building age must be between 0 and 200 years")
        validated['building_age'] = building_age
        
        # Insulation level
        insulation = float(config.get('insulation_level', 0.7))
        if not 0.0 <= insulation <= 1.0:
            raise ValueError("Insulation level must be between 0.0 and 1.0")
        validated['insulation_level'] = insulation
        
        # HVAC efficiency
        hvac_eff = float(config.get('hvac_efficiency', 0.8))
        if not 0.1 <= hvac_eff <= 1.0:
            raise ValueError("HVAC efficiency must be between 0.1 and 1.0")
        validated['hvac_efficiency'] = hvac_eff
        
        # Occupancy max
        occupancy_max = int(config.get('occupancy_max', 100))
        if not 1 <= occupancy_max <= 10000:
            raise ValueError("Max occupancy must be between 1 and 10,000")
        validated['occupancy_max'] = occupancy_max
        
        # Renewable energy
        validated['renewable_energy'] = bool(config.get('renewable_energy', False))
        
        return validated
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> tuple:
        """Validate date range."""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        if start >= end:
            raise ValueError("Start date must be before end date")
        
        # Limit range to prevent abuse
        days_diff = (end - start).days
        if days_diff > 365:
            raise ValueError("Date range cannot exceed 365 days")
        
        if start < datetime.now() - timedelta(days=1095):  # 3 years
            raise ValueError("Start date cannot be more than 3 years ago")
        
        return start, end
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        
        # Remove potentially dangerous characters
        sanitized = ''.join(char for char in value if char.isprintable())
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()

# Audit logging
class AuditLogger:
    """Audit logging for security events."""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    def log_login_attempt(self, username: str, ip_address: str, success: bool):
        """Log login attempt."""
        event = "LOGIN_SUCCESS" if success else "LOGIN_FAILURE"
        self.logger.info(f"{event} | User: {username} | IP: {ip_address}")
    
    def log_api_access(self, user_id: int, endpoint: str, ip_address: str):
        """Log API access."""
        self.logger.info(f"API_ACCESS | User: {user_id} | Endpoint: {endpoint} | IP: {ip_address}")
    
    def log_data_access(self, user_id: int, building_id: int, action: str):
        """Log data access."""
        self.logger.info(f"DATA_ACCESS | User: {user_id} | Building: {building_id} | Action: {action}")
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security event."""
        self.logger.warning(f"SECURITY_EVENT | Type: {event_type} | Details: {details}")

# Security utilities
def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename."""
    # Remove path components
    filename = os.path.basename(original_filename)
    
    # Remove potentially dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    filename = ''.join(char for char in filename if char in safe_chars)
    
    # Add timestamp to prevent conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    
    return f"{name}_{timestamp}{ext}"

def validate_file_upload(file_content: bytes, allowed_types: List[str] = None) -> bool:
    """Validate uploaded file."""
    if allowed_types is None:
        allowed_types = ['csv', 'json', 'xlsx']
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024
    if len(file_content) > max_size:
        raise ValueError("File too large. Maximum size is 10MB")
    
    # Basic content validation
    if len(file_content) == 0:
        raise ValueError("Empty file not allowed")
    
    return True

def check_permissions(user: User, action: str, resource_type: str, resource_id: Optional[int] = None) -> bool:
    """Check user permissions for action."""
    # Superuser can do everything
    if user.is_superuser:
        return True
    
    # Check if user is active
    if not user.is_active:
        return False
    
    # Basic permission checks
    if action == "read" and resource_type == "building":
        # Users can read their own buildings
        return True
    
    if action == "create" and resource_type == "building":
        # Check building quota
        # In production, check actual count from database
        return True  # Simplified for demo
    
    if action == "optimize" and resource_type == "building":
        # Users can optimize their buildings
        return True
    
    # Default deny
    return False

# Middleware for request logging
class SecurityMiddleware:
    """Security middleware for FastAPI."""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
    
    async def __call__(self, request: Request, call_next):
        """Process request with security checks."""
        start_time = time.time()
        client_ip = request.client.host
        
        # Log request
        self.audit_logger.log_api_access(
            user_id=0,  # Will be updated if authenticated
            endpoint=request.url.path,
            ip_address=client_ip
        )
        
        # Check rate limit
        try:
            await rate_limit_middleware(request)
        except HTTPException as e:
            # Log rate limit violation
            self.audit_logger.log_security_event("RATE_LIMIT_EXCEEDED", {
                "ip": client_ip,
                "endpoint": request.url.path
            })
            raise e
        
        response = await call_next(request)
        
        # Log response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

# API Key authentication
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Verify API key authentication."""
    api_key = credentials.credentials
    
    # In production, check against database
    # For demo, accept keys starting with "eo_"
    if not api_key.startswith("eo_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    # Return demo user
    return User(
        id=1,
        username="api_user",
        email="api@example.com",
        is_active=True,
        created_at=datetime.utcnow(),
        buildings_quota=100,
        api_calls_quota=10000
    )

# Security headers middleware
def add_security_headers(response):
    """Add security headers to response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Password strength validator
def validate_password_strength(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        raise ValueError("Password must contain at least one special character")
    
    return True

if __name__ == "__main__":
    # Test security functions
    print("🔐 Testing security system...")
    
    # Test password hashing
    manager = SecurityManager()
    password = "TestPassword123!"
    
    try:
        validate_password_strength(password)
        print("✅ Password validation passed")
    except ValueError as e:
        print(f"❌ Password validation failed: {e}")
    
    hashed = manager.get_password_hash(password)
    verified = manager.verify_password(password, hashed)
    print(f"✅ Password hashing works: {verified}")
    
    # Test token creation
    token_data = {"sub": "1", "username": "testuser"}
    access_token = manager.create_access_token(token_data)
    refresh_token = manager.create_refresh_token(token_data)
    
    print(f"✅ Tokens created successfully")
    
    # Test token verification
    try:
        payload = manager.verify_token(access_token)
        print(f"✅ Token verification passed: {payload['username']}")
    except HTTPException as e:
        print(f"❌ Token verification failed: {e}")
    
    # Test API key generation
    api_key, key_hash = manager.generate_api_key(1, "test_key")
    verified_key = manager.verify_api_key(api_key, key_hash)
    print(f"✅ API key generation and verification: {verified_key}")
    
    print("🔒 Security system test complete!")
