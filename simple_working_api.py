#!/usr/bin/env python3
"""
Quick API Server for Testing
Simple FastAPI server that works with current structure
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PakWheels API",
    description="Car price prediction and analysis API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class CarData(BaseModel):
    brand: Optional[str] = "Toyota"
    model: Optional[str] = "Corolla"
    year: Optional[int] = 2020
    mileage: Optional[int] = 50000
    engine_capacity: Optional[float] = 1.8
    fuel_type: Optional[str] = "Petrol"
    transmission: Optional[str] = "Manual"

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence: float
    brand: str
    model: str
    year: int

# Load sample data
try:
    # Try to load enhanced data
    data_file = "enhanced_car_data.csv"
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        logger.info(f"Loaded data: {df.shape}")
    else:
        # Create sample data if file doesn't exist
        df = pd.DataFrame({
            'brand': ['Toyota', 'Honda', 'Suzuki', 'Nissan'] * 100,
            'model': ['Corolla', 'Civic', 'Alto', 'Sunny'] * 100,
            'year': np.random.randint(2010, 2024, 400),
            'price': np.random.randint(500000, 5000000, 400),
            'mileage': np.random.randint(10000, 200000, 400)
        })
        logger.info("Using sample data")
        
except Exception as e:
    logger.error(f"Error loading data: {e}")
    df = pd.DataFrame()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PakWheels API is running!",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": len(df) > 0,
        "data_rows": len(df)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_price(car_data: CarData):
    """Predict car price"""
    try:
        # Simple prediction logic using average prices
        if len(df) > 0:
            # Filter by brand if available
            brand_data = df[df['brand'].str.lower() == car_data.brand.lower()]
            
            if len(brand_data) > 0:
                # Calculate average price for the brand
                avg_price = brand_data['price'].mean()
                
                # Adjust for year (newer cars are more expensive)
                year_factor = 1 + (car_data.year - 2015) * 0.05
                
                # Adjust for mileage (higher mileage = lower price)
                mileage_factor = 1 - (car_data.mileage / 200000) * 0.3
                
                predicted_price = avg_price * year_factor * mileage_factor
                confidence = 0.75
            else:
                # Default prediction if brand not found
                predicted_price = 1500000  # Default price
                confidence = 0.50
        else:
            # Fallback prediction
            base_price = 1000000
            year_factor = 1 + (car_data.year - 2015) * 0.08
            mileage_factor = 1 - (car_data.mileage / 200000) * 0.25
            
            predicted_price = base_price * year_factor * mileage_factor
            confidence = 0.60
        
        return PredictionResponse(
            predicted_price=float(predicted_price),
            confidence=float(confidence),
            brand=car_data.brand,
            model=car_data.model,
            year=car_data.year
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/cars")
async def get_cars(limit: int = 10):
    """Get list of cars"""
    try:
        if len(df) > 0:
            sample_cars = df.head(limit).to_dict('records')
            return {
                "cars": sample_cars,
                "total": len(df),
                "showing": min(limit, len(df))
            }
        else:
            return {
                "cars": [],
                "total": 0,
                "showing": 0,
                "message": "No car data available"
            }
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving cars: {str(e)}")

@app.get("/brands")
async def get_brands():
    """Get list of available brands"""
    try:
        if len(df) > 0:
            brands = df['brand'].unique().tolist()
            return {
                "brands": brands,
                "count": len(brands)
            }
        else:
            return {
                "brands": ["Toyota", "Honda", "Suzuki", "Nissan", "Hyundai"],
                "count": 5,
                "message": "Default brands (no data loaded)"
            }
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving brands: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get basic statistics"""
    try:
        if len(df) > 0:
            stats = {
                "total_cars": len(df),
                "unique_brands": df['brand'].nunique() if 'brand' in df.columns else 0,
                "avg_price": float(df['price'].mean()) if 'price' in df.columns else 0,
                "price_range": {
                    "min": float(df['price'].min()) if 'price' in df.columns else 0,
                    "max": float(df['price'].max()) if 'price' in df.columns else 0
                } if 'price' in df.columns else {"min": 0, "max": 0}
            }
        else:
            stats = {
                "total_cars": 0,
                "unique_brands": 0,
                "avg_price": 0,
                "price_range": {"min": 0, "max": 0},
                "message": "No data available"
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
