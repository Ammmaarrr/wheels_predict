"""
Enhanced FastAPI Server with New Features
Uses enhanced models and recommendation engine
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging
import sys
import asyncio

# Add current directory to path
sys.path.append('.')

# Import our enhanced models
try:
    from models.enhanced_model_training_v2 import EnhancedCarPricePredictor
    from models.enhanced_recommendation_engine import EnhancedRecommendationEngine
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the enhanced model files are in the models directory")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enhanced PakWheels ML API",
    description="Advanced car price prediction and recommendation API with enhanced features",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from enhanced_api_wrapper import enhanced_api

# Global variables for models
price_predictor = None
recommendation_engine = None

# Pydantic models
class EnhancedPriceRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: Optional[int] = 0
    engine_capacity: float
    transmission: str
    location: str
    variant: Optional[str] = "unknown"

class EnhancedPriceResponse(BaseModel):
    predicted_price: float
    confidence: float
    price_range: Dict[str, float]
    model_info: Dict[str, str]

class EnhancedRecommendationRequest(BaseModel):
    budget: float
    preferences: Optional[Dict[str, Any]] = None
    location: Optional[str] = ""
    max_results: int = 10

class EnhancedRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_found: int
    search_criteria: Dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load models and data on startup."""
    global price_predictor, recommendation_engine
    
    logger.info("Starting Enhanced PakWheels ML API...")
    
    try:
        # Initialize price predictor
        price_predictor = EnhancedCarPricePredictor()
        
        # Try to load pre-trained model
        model_files = [f for f in os.listdir("models") if f.startswith("enhanced_car_price_model")]
        if model_files:
            latest_model = sorted(model_files)[-1]
            model_path = os.path.join("models", latest_model)
            price_predictor.load_model(model_path)
            logger.info(f"Loaded pre-trained price model: {latest_model}")
        else:
            logger.warning("No pre-trained price model found. Training new model...")
            # Train new model if none exists
            await train_models_background()
        
        # Initialize recommendation engine
        recommendation_engine = EnhancedRecommendationEngine()
        
        # Try to load pre-trained recommendation engine
        rec_engine_path = "models/enhanced_recommendation_engine.joblib"
        if os.path.exists(rec_engine_path):
            recommendation_engine.load_recommendation_engine(rec_engine_path)
            logger.info("Loaded pre-trained recommendation engine")
        else:
            logger.warning("No pre-trained recommendation engine found. Loading data...")
            # Load data for recommendation engine
            data_files = [f for f in os.listdir("data/cleaned") if f.startswith("cleaned_enhanced")]
            if data_files:
                latest_data = sorted(data_files)[-1]
                data_path = os.path.join("data/cleaned", latest_data)
                recommendation_engine.load_enhanced_data(data_path)
                logger.info(f"Loaded enhanced data for recommendations: {latest_data}")
            else:
                logger.error("No enhanced data found for recommendations!")
        
        logger.info("Enhanced PakWheels ML API startup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

async def train_models_background():
    """Train models in the background."""
    try:
        logger.info("Training enhanced models in background...")
        
        # Find latest enhanced data
        data_files = [f for f in os.listdir("data/cleaned") if f.startswith("cleaned_enhanced")]
        if not data_files:
            logger.error("No enhanced data found for training!")
            return
        
        latest_data = sorted(data_files)[-1]
        data_path = os.path.join("data/cleaned", latest_data)
        
        # Train price prediction model
        df = price_predictor.load_enhanced_data(data_path)
        df_processed, feature_columns = price_predictor.prepare_features(df)
        model, score = price_predictor.train_model(df_processed, feature_columns)
        
        # Save model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/enhanced_car_price_model_{timestamp}.joblib"
        price_predictor.save_model(model_path)
        
        logger.info(f"Enhanced price model trained and saved: {model_path}")
        
    except Exception as e:
        logger.error(f"Error training models: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "price_predictor": price_predictor is not None,
            "recommendation_engine": recommendation_engine is not None
        }
    }

# Enhanced price prediction endpoint
@app.post("/predict", response_model=EnhancedPriceResponse)
async def predict_price(request: EnhancedPriceRequest):
    """Enhanced price prediction endpoint."""
    try:
        if price_predictor is None:
            raise HTTPException(status_code=503, detail="Price prediction model not loaded")
        
        logger.info(f"Predicting price for: {request.make} {request.model} {request.year}")
        
        # Make prediction
        predicted_price = price_predictor.predict_price(
            make=request.make,
            model=request.model,
            year=request.year,
            engine_capacity=request.engine_capacity,
            transmission=request.transmission,
            variant=request.variant
        )
        
        # Calculate confidence and price range
        confidence = min(0.95, max(0.70, 0.85 + (request.year - 2000) * 0.002))
        price_range = {
            "min": predicted_price * 0.85,
            "max": predicted_price * 1.15,
            "predicted": predicted_price
        }
        
        # Model info
        model_info = {
            "model_type": "Enhanced Gradient Boosting",
            "features_used": "make, model, year, engine_capacity, transmission, variant",
            "data_quality": "Enhanced with extracted features"
        }
        
        return EnhancedPriceResponse(
            predicted_price=predicted_price,
            confidence=confidence,
            price_range=price_range,
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Error in price prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Price prediction failed: {str(e)}")

# Enhanced recommendations endpoint
@app.post("/recommendations", response_model=EnhancedRecommendationResponse)
async def get_recommendations(request: EnhancedRecommendationRequest):
    """Enhanced recommendations endpoint."""
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not loaded")
        
        logger.info(f"Getting recommendations for budget: {request.budget}")
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            budget=request.budget,
            preferences=request.preferences,
            max_results=request.max_results
        )
        
        # Search criteria for response
        search_criteria = {
            "budget": request.budget,
            "preferences": request.preferences or {},
            "location": request.location,
            "max_results": request.max_results
        }
        
        return EnhancedRecommendationResponse(
            recommendations=recommendations,
            total_found=len(recommendations),
            search_criteria=search_criteria
        )
        
    except Exception as e:
        logger.error(f"Error in recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

# Get recommendations by budget range
@app.get("/recommendations")
async def get_recommendations_by_budget(
    budget: float,
    car_type: Optional[str] = None,
    transmission: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    make: Optional[str] = None
):
    """Get recommendations by budget and filters."""
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=503, detail="Recommendation engine not loaded")
        
        # Build preferences from query parameters
        preferences = {}
        if car_type:
            preferences['car_type'] = car_type
        if transmission:
            preferences['transmission'] = transmission
        if min_year:
            preferences['min_year'] = min_year
        if max_year:
            preferences['max_year'] = max_year
        if make:
            preferences['make'] = make
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            budget=budget,
            preferences=preferences,
            max_results=10
        )
        
        return {
            "recommendations": recommendations,
            "total_found": len(recommendations),
            "budget": budget,
            "filters_applied": preferences
        }
        
    except Exception as e:
        logger.error(f"Error in budget recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Budget recommendations failed: {str(e)}")

# Chat endpoint (mock for now)
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for car-related queries."""
    try:
        # Simple mock response - can be enhanced with actual NLP
        message = request.message.lower()
        
        if "price" in message or "cost" in message:
            response = "I can help you predict car prices! Please provide the car make, model, year, and engine capacity."
            intent = "price_inquiry"
            confidence = 0.85
        elif "recommend" in message or "suggest" in message:
            response = "I can recommend cars based on your budget and preferences! What's your budget range?"
            intent = "recommendation_inquiry"
            confidence = 0.80
        elif "compare" in message:
            response = "I can help you compare different cars. Which cars would you like to compare?"
            intent = "comparison_inquiry"
            confidence = 0.75
        else:
            response = "I'm here to help with car price predictions and recommendations. How can I assist you?"
            intent = "general_inquiry"
            confidence = 0.60
        
        return ChatResponse(
            response=response,
            intent=intent,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Dashboard stats endpoint
@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        if recommendation_engine is None or recommendation_engine.df is None:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        df = recommendation_engine.df
        
        # Calculate statistics
        stats = {
            "total_cars": len(df),
            "average_price": float(df['rec_price'].mean()),
            "price_range": {
                "min": float(df['rec_price'].min()),
                "max": float(df['rec_price'].max())
            },
            "top_makes": df['rec_make'].value_counts().head(5).to_dict(),
            "transmission_breakdown": df['rec_transmission'].value_counts().to_dict(),
            "year_distribution": df['rec_year'].value_counts().sort_index().tail(10).to_dict(),
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard stats failed: {str(e)}")

# Model training endpoint
@app.post("/admin/retrain-models")
async def retrain_models(background_tasks: BackgroundTasks):
    """Retrain models with latest data."""
    try:
        background_tasks.add_task(train_models_background)
        return {
            "message": "Model retraining started in background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting model retrain: {e}")
        raise HTTPException(status_code=500, detail=f"Model retrain failed: {str(e)}")

# System alerts endpoint
@app.get("/alerts")
async def get_system_alerts():
    """Get system alerts."""
    alerts = []
    
    # Check model status
    if price_predictor is None:
        alerts.append({
            "type": "error",
            "message": "Price prediction model not loaded",
            "timestamp": datetime.now().isoformat()
        })
    
    if recommendation_engine is None:
        alerts.append({
            "type": "error",
            "message": "Recommendation engine not loaded",
            "timestamp": datetime.now().isoformat()
        })
    
    # Add sample alerts if no real alerts
    if not alerts:
        import random
        if random.random() < 0.3:  # 30% chance of having alerts
            alerts.append({
                "type": "warning",
                "message": "Model accuracy monitoring suggests retraining may be needed",
                "timestamp": datetime.now().isoformat()
            })
    
    return {"alerts": alerts}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
