"""
Modern FastAPI backend for PakWheels data scraping and ML project.
Provides RESTful API endpoints for the React frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
from pathlib import Path
import uvicorn
import logging
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import modules
from utils.logger import setup_logger, log_error
from models.model_monitor import ModelMonitor
from models.recommendation_engine import predict_price, get_similar_cars, enhanced_hybrid_recommendation
from flows.conversation_manager import handle_user_message
from data_processing.clean_and_preprocess import DataProcessor

# Set up logger
logger = setup_logger(__name__)

# Pydantic models for request/response
class PriceRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: int
    engine_type: str
    transmission: str
    location: str
    features: Optional[List[str]] = []

class RecommendationRequest(BaseModel):
    budget: float
    preferences: Dict[str, Any]
    location: Optional[str] = None
    max_results: Optional[int] = 10

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class RetrainRequest(BaseModel):
    force: Optional[bool] = False
    models: Optional[List[str]] = None

# Global instances
model_monitor = None
recommendation_engine = None
data_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global model_monitor, recommendation_engine, data_processor
    
    try:
        # Initialize components
        logger.info("Initializing FastAPI application...")
        
        model_monitor = ModelMonitor()
        data_processor = DataProcessor()
        
        logger.info("FastAPI application initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down FastAPI application...")

# Create FastAPI app
app = FastAPI(
    title="PakWheels Data Scraping & ML API",
    description="Modern API for car price prediction, recommendations, and monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React build
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API Routes
@app.get("/api/v1/status")
async def get_system_status():
    """Get overall system status."""
    try:
        status = {
            "system": "healthy",
            "models": model_monitor.get_model_status() if model_monitor else "unavailable",
            "database": "connected",  # TODO: Add actual DB check
            "scraping": "operational",
            "timestamp": datetime.now().isoformat()
        }
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@app.post("/api/v1/predict")
async def predict_price(request: PriceRequest):
    """Predict car price based on features."""
    try:
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="Recommendation engine not available")
        
        # Convert request to format expected by recommendation engine
        car_data = {
            'make': request.make,
            'model': request.model,
            'year': request.year,
            'mileage': request.mileage,
            'engine_type': request.engine_type,
            'transmission': request.transmission,
            'location': request.location,
            'features': request.features
        }
        
        # Get prediction
        prediction = recommendation_engine.predict_price(car_data)
        
        # Log prediction for monitoring
        if model_monitor:
            await asyncio.to_thread(model_monitor.log_prediction, car_data, prediction)
        
        return {
            "predicted_price": prediction,
            "confidence": "high",  # TODO: Add actual confidence calculation
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict price")

@app.post("/api/v1/recommend")
async def get_recommendations(request: RecommendationRequest):
    """Get car recommendations based on budget and preferences."""
    try:
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="Recommendation engine not available")
        
        recommendations = recommendation_engine.get_recommendations(
            budget=request.budget,
            preferences=request.preferences,
            location=request.location,
            max_results=request.max_results
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@app.post("/api/v1/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat with AI assistant."""
    try:
        response = handle_user_message(request.message, request.session_id)
        
        return {
            "response": response,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

# Monitoring endpoints
@app.get("/api/v1/monitoring/metrics")
async def get_monitoring_metrics():
    """Get current monitoring metrics."""
    try:
        if not model_monitor:
            raise HTTPException(status_code=503, detail="Model monitor not available")
        
        metrics = model_monitor.get_current_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get monitoring metrics")

@app.get("/api/v1/monitoring/performance")
async def get_performance_metrics():
    """Get model performance metrics."""
    try:
        if not model_monitor:
            raise HTTPException(status_code=503, detail="Model monitor not available")
        
        performance = model_monitor.get_performance_metrics()
        return performance
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@app.get("/api/v1/monitoring/alerts")
async def get_alerts():
    """Get current alerts."""
    try:
        if not model_monitor:
            raise HTTPException(status_code=503, detail="Model monitor not available")
        
        alerts = model_monitor.get_alerts()
        return {"alerts": alerts, "count": len(alerts)}
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@app.post("/api/v1/monitoring/retrain")
async def trigger_retrain(request: RetrainRequest, background_tasks: BackgroundTasks):
    """Trigger model retraining."""
    try:
        if not model_monitor:
            raise HTTPException(status_code=503, detail="Model monitor not available")
        
        # Start retraining in background
        background_tasks.add_task(
            model_monitor.retrain_models,
            force=request.force,
            models=request.models
        )
        
        return {
            "message": "Model retraining started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering retrain: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger retraining")

# Data endpoints
@app.get("/api/v1/data/stats")
async def get_data_stats():
    """Get dataset statistics."""
    try:
        if not data_processor:
            raise HTTPException(status_code=503, detail="Data processor not available")
        
        stats = data_processor.get_dataset_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data statistics")

@app.get("/api/v1/data/recent")
async def get_recent_data(limit: int = 100):
    """Get recent data entries."""
    try:
        if not data_processor:
            raise HTTPException(status_code=503, detail="Data processor not available")
        
        recent_data = data_processor.get_recent_data(limit)
        return {
            "data": recent_data,
            "count": len(recent_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent data")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
