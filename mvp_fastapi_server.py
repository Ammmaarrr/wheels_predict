"""
MVP FastAPI Server for Wheels Predict API
Enhanced with user authentication and dealer-specific features
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import logging
import sys
import asyncio
import jwt
import bcrypt
import json
from pathlib import Path

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

# JWT Configuration
SECRET_KEY = "your-secret-key-for-jwt-tokens"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create FastAPI app
app = FastAPI(
    title="Wheels Predict API - MVP",
    description="Advanced car price prediction and recommendation API for dealers and resellers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global variables for models
price_predictor = None
recommendation_engine = None

# User database (in production, use a real database)
users_db_path = "config/users.json"
users_db = {}

# Load users database
def load_users_db():
    global users_db
    if os.path.exists(users_db_path):
        with open(users_db_path, 'r') as f:
            users_db = json.load(f)
    else:
        # Create default users for MVP
        users_db = {
            "dealer1@example.com": {
                "email": "dealer1@example.com",
                "hashed_password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "user_type": "dealer",
                "name": "ABC Motors",
                "location": "Karachi",
                "verified": True,
                "api_calls": 0,
                "max_api_calls": 1000
            },
            "reseller1@example.com": {
                "email": "reseller1@example.com",
                "hashed_password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "user_type": "reseller",
                "name": "Quick Cars",
                "location": "Lahore",
                "verified": True,
                "api_calls": 0,
                "max_api_calls": 500
            },
            "admin@wheelspredict.com": {
                "email": "admin@wheelspredict.com",
                "hashed_password": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "user_type": "admin",
                "name": "Admin User",
                "location": "Islamabad",
                "verified": True,
                "api_calls": 0,
                "max_api_calls": 10000
            }
        }
        save_users_db()

def save_users_db():
    os.makedirs(os.path.dirname(users_db_path), exist_ok=True)
    with open(users_db_path, 'w') as f:
        json.dump(users_db, f, indent=2)

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    user_type: str  # "dealer" or "reseller"
    location: str
    phone: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]

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
    market_insights: Optional[Dict[str, Any]] = None

class DealerRecommendationRequest(BaseModel):
    budget_min: float
    budget_max: float
    preferences: Optional[Dict[str, Any]] = None
    location: Optional[str] = ""
    max_results: int = 10
    sort_by: str = "price"  # "price", "value", "popularity"

class DealerRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_found: int
    search_criteria: Dict[str, Any]
    market_summary: Dict[str, Any]

class MarketAnalysisRequest(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year_range: Optional[List[int]] = None
    location: Optional[str] = None
    time_period: str = "last_30_days"

class MarketAnalysisResponse(BaseModel):
    market_trends: Dict[str, Any]
    price_analysis: Dict[str, Any]
    inventory_insights: Dict[str, Any]
    recommendations: List[str]

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(email: str = Depends(verify_token)):
    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[email]

def check_api_limit(user: dict):
    if user["api_calls"] >= user["max_api_calls"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API call limit exceeded"
        )

def increment_api_calls(user: dict):
    user["api_calls"] += 1
    save_users_db()

# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user (dealer or reseller)"""
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate user type
    if user.user_type not in ["dealer", "reseller"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User type must be 'dealer' or 'reseller'"
        )
    
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Set API limits based on user type
    max_calls = 1000 if user.user_type == "dealer" else 500
    
    # Create user
    users_db[user.email] = {
        "email": user.email,
        "hashed_password": hashed_password,
        "user_type": user.user_type,
        "name": user.name,
        "location": user.location,
        "phone": user.phone,
        "verified": True,  # Auto-verify for MVP
        "api_calls": 0,
        "max_api_calls": max_calls,
        "created_at": datetime.utcnow().isoformat()
    }
    
    save_users_db()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "email": user.email,
            "name": user.name,
            "user_type": user.user_type,
            "location": user.location,
            "api_calls": 0,
            "max_api_calls": max_calls
        }
    }

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    """Login user and get access token"""
    if user.email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_data = users_db[user.email]
    
    # Verify password
    if not bcrypt.checkpw(user.password.encode('utf-8'), user_data["hashed_password"].encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "email": user_data["email"],
            "name": user_data["name"],
            "user_type": user_data["user_type"],
            "location": user_data["location"],
            "api_calls": user_data["api_calls"],
            "max_api_calls": user_data["max_api_calls"]
        }
    }

@app.get("/auth/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "email": current_user["email"],
        "name": current_user["name"],
        "user_type": current_user["user_type"],
        "location": current_user["location"],
        "api_calls": current_user["api_calls"],
        "max_api_calls": current_user["max_api_calls"],
        "phone": current_user.get("phone"),
        "verified": current_user["verified"]
    }

# Enhanced API endpoints
@app.post("/api/predict-price", response_model=EnhancedPriceResponse)
async def predict_price(
    request: EnhancedPriceRequest,
    current_user: dict = Depends(get_current_user)
):
    """Predict car price with enhanced features"""
    check_api_limit(current_user)
    
    try:
        if price_predictor is None:
            raise HTTPException(status_code=500, detail="Price prediction model not available")
        
        # Make prediction
        prediction = price_predictor.predict_price(
            make=request.make,
            model=request.model,
            year=request.year,
            mileage=request.mileage,
            engine_capacity=request.engine_capacity,
            transmission=request.transmission,
            location=request.location,
            variant=request.variant
        )
        
        # Add market insights for dealers
        market_insights = None
        if current_user["user_type"] == "dealer":
            market_insights = {
                "demand_score": np.random.uniform(0.6, 0.9),
                "inventory_level": np.random.choice(["low", "medium", "high"]),
                "price_trend": np.random.choice(["rising", "stable", "falling"]),
                "regional_demand": f"High demand in {request.location}"
            }
        
        increment_api_calls(current_user)
        
        return EnhancedPriceResponse(
            predicted_price=prediction["predicted_price"],
            confidence=prediction["confidence"],
            price_range=prediction["price_range"],
            model_info=prediction["model_info"],
            market_insights=market_insights
        )
        
    except Exception as e:
        logger.error(f"Price prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/dealer-recommendations", response_model=DealerRecommendationResponse)
async def get_dealer_recommendations(
    request: DealerRecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get recommendations optimized for dealers"""
    check_api_limit(current_user)
    
    try:
        if recommendation_engine is None:
            raise HTTPException(status_code=500, detail="Recommendation engine not available")
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            budget=request.budget_max,
            preferences=request.preferences or {},
            location=request.location,
            max_results=request.max_results
        )
        
        # Add dealer-specific insights
        for rec in recommendations["recommendations"]:
            if current_user["user_type"] == "dealer":
                rec["profit_margin"] = np.random.uniform(0.1, 0.3)
                rec["turnover_days"] = np.random.randint(15, 60)
                rec["demand_score"] = np.random.uniform(0.5, 0.9)
        
        # Market summary for dealers
        market_summary = {
            "total_inventory": len(recommendations["recommendations"]),
            "avg_price": np.mean([r["price"] for r in recommendations["recommendations"]]),
            "price_range": {
                "min": min([r["price"] for r in recommendations["recommendations"]]),
                "max": max([r["price"] for r in recommendations["recommendations"]])
            },
            "top_makes": ["Toyota", "Honda", "Suzuki"]  # Mock data
        }
        
        increment_api_calls(current_user)
        
        return DealerRecommendationResponse(
            recommendations=recommendations["recommendations"],
            total_found=recommendations["total_found"],
            search_criteria=recommendations["search_criteria"],
            market_summary=market_summary
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@app.post("/api/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    request: MarketAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get market analysis (premium feature for dealers)"""
    check_api_limit(current_user)
    
    if current_user["user_type"] not in ["dealer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Market analysis is only available for dealers"
        )
    
    try:
        # Mock market analysis data
        market_trends = {
            "price_trend": "stable",
            "volume_trend": "increasing",
            "seasonal_factor": 1.05,
            "market_growth": 0.08
        }
        
        price_analysis = {
            "avg_price": 2500000,
            "price_change_30d": 0.03,
            "price_volatility": 0.15,
            "value_score": 0.75
        }
        
        inventory_insights = {
            "total_listings": 1250,
            "new_listings_7d": 45,
            "avg_days_on_market": 28,
            "turnover_rate": 0.12
        }
        
        recommendations = [
            "Consider stocking more compact cars for urban areas",
            "SUVs showing strong demand in current market",
            "Automatic transmission vehicles preferred by 70% of buyers"
        ]
        
        increment_api_calls(current_user)
        
        return MarketAnalysisResponse(
            market_trends=market_trends,
            price_analysis=price_analysis,
            inventory_insights=inventory_insights,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Market analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Market analysis error: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Get dashboard data for user"""
    try:
        dashboard_data = {
            "user_stats": {
                "api_calls_today": current_user["api_calls"],
                "remaining_calls": current_user["max_api_calls"] - current_user["api_calls"],
                "usage_percentage": (current_user["api_calls"] / current_user["max_api_calls"]) * 100
            },
            "quick_stats": {
                "total_listings": 1250,
                "avg_price": 2500000,
                "popular_makes": ["Toyota", "Honda", "Suzuki"],
                "locations": ["Karachi", "Lahore", "Islamabad"]
            }
        }
        
        # Add dealer-specific data
        if current_user["user_type"] == "dealer":
            dashboard_data["dealer_insights"] = {
                "market_opportunities": 5,
                "trending_models": ["Corolla", "Civic", "Alto"],
                "profit_opportunities": 3
            }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

# Public endpoints (no auth required)
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wheels Predict API - MVP",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "auth": ["/auth/register", "/auth/login", "/auth/profile"],
            "api": ["/api/predict-price", "/api/dealer-recommendations", "/api/market-analysis", "/api/dashboard"]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models": {
            "price_predictor": price_predictor is not None,
            "recommendation_engine": recommendation_engine is not None
        }
    }

@app.get("/api/demo-credentials")
async def get_demo_credentials():
    """Get demo credentials for testing"""
    return {
        "demo_accounts": [
            {
                "email": "dealer1@example.com",
                "password": "password123",
                "type": "dealer",
                "name": "ABC Motors"
            },
            {
                "email": "reseller1@example.com",
                "password": "password123",
                "type": "reseller",
                "name": "Quick Cars"
            }
        ],
        "note": "Use these credentials to test the API"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load models and data on startup."""
    global price_predictor, recommendation_engine
    
    logger.info("Starting Wheels Predict API - MVP...")
    
    # Load users database
    load_users_db()
    
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
            logger.warning("No pre-trained price model found. Will use mock predictions.")
        
        # Initialize recommendation engine
        recommendation_engine = EnhancedRecommendationEngine()
        
        # Try to load pre-trained recommendation engine
        rec_engine_path = "models/enhanced_recommendation_engine.joblib"
        if os.path.exists(rec_engine_path):
            recommendation_engine.load_recommendation_engine(rec_engine_path)
            logger.info("Loaded pre-trained recommendation engine")
        else:
            logger.warning("No pre-trained recommendation engine found. Will use mock recommendations.")
        
        logger.info("Wheels Predict API - MVP startup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't raise, continue with mock data for MVP
        logger.info("Continuing with mock data for MVP demonstration")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
