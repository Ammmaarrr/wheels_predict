#!/usr/bin/env python3
"""
Simple FastAPI server for PakWheels ML Platform
This is a minimal version to get the API running quickly
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create FastAPI app
app = FastAPI(
    title="PakWheels ML Platform - Simple API",
    description="A simplified API for car price prediction and recommendations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class PriceRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: int
    engine_capacity: float
    transmission: str
    location: str

class PriceResponse(BaseModel):
    predicted_price: float
    confidence: float
    message: str

class SystemStatus(BaseModel):
    status: str
    message: str
    timestamp: str

# Mock data for demonstration
MOCK_PRICE_DATA = {
    "toyota": {"corolla": 1500000, "camry": 2500000, "prius": 2000000},
    "honda": {"civic": 1800000, "accord": 2200000, "city": 1200000},
    "suzuki": {"cultus": 1100000, "swift": 1300000, "mehran": 800000},
}

@app.get("/")
async def root():
    return {"message": "PakWheels ML Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/status")
async def get_system_status():
    return SystemStatus(
        status="healthy",
        message="System is running normally",
        timestamp="2025-07-09T22:00:00Z"
    )

@app.post("/api/predict", response_model=PriceResponse)
async def predict_price(request: PriceRequest):
    try:
        # Simple mock prediction based on make and model
        make_lower = request.make.lower()
        model_lower = request.model.lower()
        
        base_price = MOCK_PRICE_DATA.get(make_lower, {}).get(model_lower, 1500000)
        
        # Apply some basic adjustments
        year_factor = max(0.5, (request.year - 2000) / 25)  # Newer cars worth more
        mileage_factor = max(0.6, 1 - (request.mileage / 200000))  # Higher mileage worth less
        engine_factor = min(1.3, request.engine_capacity / 1000)  # Bigger engine worth more
        
        predicted_price = base_price * year_factor * mileage_factor * engine_factor
        
        return PriceResponse(
            predicted_price=round(predicted_price, 2),
            confidence=0.85,
            message="Price prediction completed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations(budget: int = 1500000):
    """Get car recommendations based on budget"""
    recommendations = []
    
    for make, models in MOCK_PRICE_DATA.items():
        for model, price in models.items():
            if price <= budget * 1.1:  # Within 10% of budget
                recommendations.append({
                    "make": make.title(),
                    "model": model.title(),
                    "estimated_price": price,
                    "score": min(100, int((budget / price) * 50))
                })
    
    # Sort by score
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    return {"recommendations": recommendations[:10]}

@app.get("/api/monitoring/metrics")
async def get_monitoring_metrics():
    """Get system monitoring metrics"""
    return {
        "prediction_count": 1247,
        "accuracy": 0.876,
        "response_time": 0.234,
        "system_health": "healthy",
        "last_updated": "2025-07-09T22:00:00Z"
    }

@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts"""
    return {
        "alerts": [
            {
                "type": "info",
                "message": "Model accuracy improved to 87.6%",
                "timestamp": "2025-07-09T21:30:00Z"
            },
            {
                "type": "warning", 
                "message": "High prediction volume detected",
                "timestamp": "2025-07-09T21:00:00Z"
            }
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
