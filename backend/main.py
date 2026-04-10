from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv
from typing import Optional

# Import custom modules
from database import get_db, init_db
from logging_config import setup_logging, setup_sentry, security_logger
from rate_limiter import limiter, RateLimits
from slowapi.errors import RateLimitExceeded

# Load environment variables first
load_dotenv()

# Setup logging and monitoring
logger = setup_logging()
setup_sentry()

# Import auth routes
try:
    from auth import router as auth_router
    logger.info("✓ Auth router loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load auth router: {e}")
    auth_router = None

# Get API key from environment (no hardcoded fallback in production)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("✗ GEMINI_API_KEY not found in environment variables!")
    raise ValueError("GEMINI_API_KEY must be set in environment")

# Configure Gemini with error handling
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-2.5-flash (available in v1beta API)
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("✓ Gemini AI configured successfully with gemini-2.5-flash")
except Exception as e:
    logger.error(f"✗ Gemini configuration failed: {e}")
    model = None

app = FastAPI(title="SIH2025 API", version="2.0.0")

# Add rate limiter state
app.state.limiter = limiter

# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    security_logger.log_event("rate_limit_exceeded", {
        "ip": request.client.host,
        "path": str(request.url.path)
    })
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "message": "Rate limit exceeded. Please try again later."
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    security_logger.log_event("unhandled_exception", {
        "ip": request.client.host,
        "path": str(request.url.path),
        "error": str(exc)
    })
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("ENVIRONMENT") != "production" else "An error occurred",
            "path": str(request.url)
        }
    )

# ✅ Enable CORS with environment-based configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and perform health checks"""
    try:
        logger.info("🚀 Starting application...")
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise

# Mount authentication routes
if auth_router:
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    logger.info("✓ Auth routes mounted")
else:
    logger.warning("⚠ Auth routes not available")

# ===============================
# 🔹 Health Check & Auto-detect server IP
# ===============================
@app.get("/")
@limiter.limit(RateLimits.HEALTH)
async def root(request: Request):
    """Root endpoint for health check"""
    return {
        "status": "online",
        "service": "SIH2025 API",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "gemini_status": "available" if model else "unavailable"
    }

@app.get("/health")
@limiter.limit(RateLimits.HEALTH)
async def health_check(request: Request, db: Session = Depends(get_db)):
    """Detailed health check endpoint with database status"""
    db_healthy = False
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "healthy" if db_healthy and model else "degraded",
        "services": {
            "database": db_healthy,
            "gemini_ai": model is not None,
            "auth": auth_router is not None
        }
    }

@app.get("/ping")
@limiter.limit(RateLimits.HEALTH)
async def ping(request: Request):
    """
    Returns the server's IP and port as seen by the client.
    Helps Flutter auto-detect backend without hardcoding.
    """
    return {
        "status": "ok",
        "server_ip": request.url.hostname,
        "server_port": request.url.port or 8000,
        "timestamp": str(requests.utils.default_headers())
    }

# ===============================
# Notes API
# ===============================
class NoteRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    board: str = Field(..., min_length=1, max_length=100)
    class_: str = Field(..., min_length=1, max_length=50)
    topic: str = Field(..., min_length=1, max_length=200)
    additionalDetail: str = Field(default="", max_length=500)
    language: str = Field(default="English", min_length=1, max_length=50)
    detailedness: float = Field(default=0.5, ge=0.0, le=1.0)

    @validator('detailedness')
    def validate_detailedness(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('detailedness must be between 0 and 1')
        return v

@app.post("/generate-note")
@limiter.limit(RateLimits.GENERATE_NOTE)
async def generate_note(req: NoteRequest, request: Request, db: Session = Depends(get_db)):
    """Generate educational notes using Gemini AI with rate limiting"""
    try:
        security_logger.log_event("note_generation_request", {
            "ip": request.client.host,
            "subject": req.subject,
            "topic": req.topic
        })
        # Security: Sanitize inputs
        req.subject = req.subject.strip()[:100]
        req.topic = req.topic.strip()[:200]
        req.additionalDetail = req.additionalDetail.strip()[:500]
        
        # Validate model availability
        if not model:
            raise HTTPException(
                status_code=503,
                detail="AI service is currently unavailable. Please try again later."
            )

        # Map detailedness slider into labels
        detail_level = (
            "Basic" if req.detailedness < 0.25 else
            "Moderate" if req.detailedness < 0.5 else
            "Detailed" if req.detailedness < 0.75 else
            "Very Detailed"
        )

        logger.info(f"Generating {detail_level} notes for {req.subject} - {req.topic}")

        # === AI Notes Generation with retry logic ===
        max_retries = 3
        note = None
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                You are a helpful teacher creating structured notes for students.
                
                Generate {detail_level} educational notes in {req.language}.
                Subject: {req.subject}
                Board/University: {req.board}
                Class/Semester: {req.class_}
                Topic: {req.topic}
                Additional details: {req.additionalDetail}
                
                Please provide well-structured, clear, and informative notes.
                """

                response = model.generate_content(prompt)
                note = response.text.strip()
                
                if not note:
                    raise ValueError("Empty response from AI")
                
                logger.info(f"✓ Notes generated successfully (attempt {attempt + 1})")
                break
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate notes after {max_retries} attempts: {str(e)}"
                    )

        return {
            "note": note,
            "detail_level": detail_level,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_note: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
