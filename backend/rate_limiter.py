"""
Rate limiting middleware for FastAPI
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

load_dotenv()

# Get rate limit from environment
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE", "30")
RATE_LIMIT_BURST = os.getenv("RATE_LIMIT_BURST", "10")

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
    strategy="fixed-window-elastic-expiry"
)

# Rate limit configurations for different endpoints
class RateLimits:
    """Rate limit configurations"""
    # Authentication endpoints (stricter)
    AUTH_LOGIN = f"{RATE_LIMIT_BURST}/minute"
    AUTH_REGISTER = f"{RATE_LIMIT_BURST}/minute"
    
    # Note generation (moderate)
    GENERATE_NOTE = f"{RATE_LIMIT_PER_MINUTE}/minute"
    
    # General API (permissive)
    GENERAL = f"{int(RATE_LIMIT_PER_MINUTE) * 2}/minute"
    
    # Health check (very permissive)
    HEALTH = "100/minute"
