#!/usr/bin/env python3
"""
Production FastAPI Server Configuration
Enhanced with production-ready features
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import aiofiles
from contextlib import asynccontextmanager

# Import your existing modules
try:
    from enhanced_api_wrapper import enhanced_api
    from models.enhanced_recommendation_engine import EnhancedRecommendationEngine
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    enhanced_api = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# Prometheus metrics
REQUEST_COUNT = Counter('pakwheels_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('pakwheels_request_duration_seconds', 'Request duration')
PREDICTION_COUNT = Counter('pakwheels_predictions_total', 'Total predictions')
RECOMMENDATION_COUNT = Counter('pakwheels_recommendations_total', 'Total recommendations')

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer(auto_error=False)

# Application state
app_state = {
    'start_time': datetime.now(),
    'requests_processed': 0,
    'predictions_made': 0,
    'recommendations_generated': 0,
    'health_status': 'healthy'
}

# Pydantic models
class PredictionRequest(BaseModel):
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., ge=1990, le=2025, description="Manufacturing year")
    engine_capacity: Optional[int] = Field(None, description="Engine capacity in CC")
    transmission: Optional[str] = Field(None, description="Transmission type")
    variant: Optional[str] = Field(None, description="Car variant")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    assembly: Optional[str] = Field(None, description="Assembly type")
    mileage: Optional[int] = Field(None, description="Mileage")
    city: Optional[str] = Field(None, description="City")

class PredictionResponse(BaseModel):
    predicted_price: float = Field(..., description="Predicted price in PKR")
    confidence: float = Field(..., description="Prediction confidence")
    price_range: Dict[str, float] = Field(..., description="Price range")
    similar_cars: List[Dict[str, Any]] = Field(default=[], description="Similar cars")
    market_insights: Dict[str, Any] = Field(default={}, description="Market insights")

class RecommendationRequest(BaseModel):
    budget: Optional[float] = Field(None, description="Budget in PKR")
    preferred_make: Optional[str] = Field(None, description="Preferred manufacturer")
    preferred_fuel: Optional[str] = Field(None, description="Preferred fuel type")
    preferred_transmission: Optional[str] = Field(None, description="Preferred transmission")
    city: Optional[str] = Field(None, description="City")
    max_age: Optional[int] = Field(None, description="Maximum car age")

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: str
    services: Dict[str, str]

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting PakWheels Production API...")
    
    # Initialize services
    if enhanced_api:
        logger.info("Loading enhanced API wrapper...")
        # Pre-load models and data
        await asyncio.to_thread(enhanced_api.load_models)
    
    logger.info("API startup complete")
    yield
    
    # Cleanup
    logger.info("Shutting down PakWheels API...")

# Create FastAPI app
app = FastAPI(
    title="PakWheels Car Price Prediction API",
    description="Production-ready API for Pakistani car market analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None,
    debug=DEBUG
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
if RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware for metrics and logging
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware for collecting metrics and logging"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(duration)
    
    # Update app state
    app_state['requests_processed'] += 1
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple authentication check"""
    if credentials is None:
        return None
    
    # In production, implement proper JWT validation
    # For now, just check if token is provided
    return {"user": "authenticated"}

# API Routes
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - app_state['start_time']
    
    # Check service health
    services = {
        "api": "healthy",
        "database": "healthy",  # Add actual database check
        "cache": "healthy",     # Add actual cache check
        "models": "healthy" if enhanced_api else "unavailable"
    }
    
    return HealthResponse(
        status=app_state['health_status'],
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=str(uptime),
        services=services
    )

@app.get("/metrics", tags=["System"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/stats", tags=["System"])
async def get_stats():
    """API statistics"""
    return {
        "requests_processed": app_state['requests_processed'],
        "predictions_made": app_state['predictions_made'],
        "recommendations_generated": app_state['recommendations_generated'],
        "uptime": str(datetime.now() - app_state['start_time']),
        "memory_usage": "Unknown",  # Add actual memory monitoring
        "cpu_usage": "Unknown"      # Add actual CPU monitoring
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
@limiter.limit("10/minute" if RATE_LIMIT_ENABLED else "1000/minute")
async def predict_price(request: Request, prediction_request: PredictionRequest):
    """Predict car price"""
    try:
        if not enhanced_api:
            raise HTTPException(status_code=503, detail="Prediction service unavailable")
        
        # Convert request to dict
        car_data = prediction_request.dict()
        
        # Make prediction
        result = await asyncio.to_thread(
            enhanced_api.predict_price_enhanced,
            **car_data
        )
        
        # Update metrics
        PREDICTION_COUNT.inc()
        app_state['predictions_made'] += 1
        
        # Enhance response with additional data
        enhanced_result = PredictionResponse(
            predicted_price=result['predicted_price'],
            confidence=result['confidence'],
            price_range={
                'min': result['predicted_price'] * 0.9,
                'max': result['predicted_price'] * 1.1
            },
            similar_cars=result.get('similar_cars', []),
            market_insights=result.get('market_insights', {})
        )
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/recommend", tags=["Recommendation"])
@limiter.limit("5/minute" if RATE_LIMIT_ENABLED else "1000/minute")
async def get_recommendations(request: Request, recommendation_request: RecommendationRequest):
    """Get car recommendations"""
    try:
        if not enhanced_api:
            raise HTTPException(status_code=503, detail="Recommendation service unavailable")
        
        # Convert request to dict
        criteria = recommendation_request.dict()
        
        # Get recommendations
        result = await asyncio.to_thread(
            enhanced_api.get_recommendations,
            **criteria
        )
        
        # Update metrics
        RECOMMENDATION_COUNT.inc()
        app_state['recommendations_generated'] += 1
        
        return result
        
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.post("/analyze", tags=["Analysis"])
@limiter.limit("3/minute" if RATE_LIMIT_ENABLED else "1000/minute")
async def analyze_market(request: Request, analysis_request: dict):
    """Analyze market trends"""
    try:
        # Implement market analysis logic
        analysis = {
            "market_trend": "stable",
            "popular_makes": ["Toyota", "Honda", "Suzuki"],
            "average_price": 2500000,
            "price_change": "+5.2%",
            "market_insights": {
                "demand": "high",
                "supply": "moderate",
                "best_time_to_buy": "current"
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/features", tags=["Information"])
async def get_features():
    """Get available features and car data"""
    try:
        if not enhanced_api or enhanced_api.enhanced_data is None:
            raise HTTPException(status_code=503, detail="Data service unavailable")
        
        df = enhanced_api.enhanced_data
        features = {
            "total_cars": len(df),
            "unique_makes": df['make'].nunique() if 'make' in df.columns else 0,
            "unique_models": df['model'].nunique() if 'model' in df.columns else 0,
            "year_range": {
                "min": int(df['year'].min()) if 'year' in df.columns else 0,
                "max": int(df['year'].max()) if 'year' in df.columns else 0
            },
            "price_range": {
                "min": float(df['price'].min()) if 'price' in df.columns else 0,
                "max": float(df['price'].max()) if 'price' in df.columns else 0
            },
            "available_features": list(df.columns) if df is not None else []
        }
        
        return features
        
    except Exception as e:
        logger.error(f"Features error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Features failed: {str(e)}")

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "PakWheels Car Price Prediction API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

# Production server configuration
if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run with production settings
    uvicorn.run(
        "enhanced_fastapi_production:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,  # Use gunicorn for multiple workers in production
        log_level="info",
        access_log=True,
        use_colors=False,
        loop="asyncio"
    )
