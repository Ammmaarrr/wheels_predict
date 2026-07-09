"""
Simple MVP FastAPI Server for Wheels Predict API
Enhanced with user authentication and dealer-specific features
Mock data for demonstration purposes
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
from datetime import datetime, timedelta
import logging
import jwt
import bcrypt
import json
import numpy as np
import random
from services.ml_model import PriceModel
from services.text_parser import parse_text_record

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "your-secret-key-for-jwt-tokens"
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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# User database (in production, use a real database)
users_db_path = "config/users.json"
users_db = {}


# Load real car data from CSV
import csv
real_car_data = []
car_data_csv_path = r"data/raw/output_2025-07-05.csv"
def load_real_car_data():
    global real_car_data
    real_car_data = []
    try:
        with open(car_data_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Parse price (remove Rs, commas, spaces)
                price_str = row['price'].replace('Rs', '').replace(',', '').strip()
                try:
                    price = int(price_str)
                except Exception:
                    price = 0
                # Parse mileage (remove km, commas, spaces)
                mileage_str = row['mileage'].replace('km', '').replace(',', '').strip()
                try:
                    mileage = int(mileage_str)
                except Exception:
                    mileage = 0
                # Parse year
                try:
                    year = int(row['year'])
                except Exception:
                    year = 0
                # Compose a more descriptive title using available fields
                make = row.get('make', '') or row.get('brand', '') or row.get('manufacturer', '')
                make = make.strip()
                model = row.get('model', '').strip()
                variant = row.get('name', '').strip()
                engine = row.get('engine', '').strip()
                year_str = row.get('year', '') or row.get('modelDate', '')
                year = year_str if year_str else ''
                title_parts = [make, model, variant, engine, str(year)]
                title = ' '.join([part for part in title_parts if part]).strip()
                # Use location if present, else empty string
                location = row.get('location', '').strip() if 'location' in row else ''
                # Use scraped_at if present, else None
                scraped_at = row.get('scraped_at', None)
                # Add ad URL if present
                url = row.get('url', '').strip() if 'url' in row else ''
                real_car_data.append({
                    'title': title,
                    'price': price,
                    'year': year,
                    'mileage': mileage,
                    'location': location,
                    'scraped_at': scraped_at,
                    'url': url
                })
    except Exception as e:
        logger.error(f"Error loading real car data: {e}")
        real_car_data = []

    # End of CSV load

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
    user_type: str
    location: str
    phone: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]

class PriceRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: Optional[int] = 0
    engine_capacity: float
    transmission: str
    location: str
    variant: Optional[str] = "unknown"

class PriceResponse(BaseModel):
    predicted_price: float
    confidence: float
    price_range: Dict[str, float]
    model_info: Dict[str, str]
    market_insights: Optional[Dict[str, Any]] = None

class RecommendationRequest(BaseModel):
    budget_min: float
    budget_max: float
    preferences: Optional[Dict[str, Any]] = None
    location: Optional[str] = ""
    max_results: int = 10

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_found: int
    market_summary: Dict[str, Any]

class MarketAnalysisRequest(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    time_period: str = "last_30_days"

class MarketAnalysisResponse(BaseModel):
    market_trends: Dict[str, Any]
    price_analysis: Dict[str, Any]
    inventory_insights: Dict[str, Any]
    recommendations: List[str]

# ML integration schemas
class ParseTextRequest(BaseModel):
    text: str

class ParseTextResponse(BaseModel):
    parsed: Dict[str, Any]

class MLPredictRequest(BaseModel):
    # Either structured features or free text; text takes precedence when provided
    text: Optional[str] = None
    features: Optional[Dict[str, Any]] = None

class MLPredictResponse(BaseModel):
    predicted_price: float
    parsed: Optional[Dict[str, Any]] = None

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

def mock_price_prediction(make: str, model: str, year: int, mileage: int, engine_capacity: float):
    """Generate mock price prediction"""
    base_price = 2000000  # Base price
    
    # Adjust for make
    make_multipliers = {"Honda": 1.2, "Toyota": 1.3, "Suzuki": 0.8, "Hyundai": 0.9}
    price = base_price * make_multipliers.get(make, 1.0)
    
    # Adjust for year
    price *= (1 + (year - 2010) * 0.05)
    
    # Adjust for mileage
    price *= (1 - mileage / 1000000)
    
    # Adjust for engine capacity
    price *= (1 + engine_capacity / 10000)
    
    # Add some randomness
    price *= random.uniform(0.9, 1.1)
    
    return {
        "predicted_price": max(price, 500000),
        "confidence": random.uniform(0.7, 0.95),
        "price_range": {
            "min": price * 0.85,
            "max": price * 1.15
        },
        "model_info": {
            "name": "Enhanced ML Model",
            "version": "v2.0",
            "accuracy": "85%"
        }
    }

def real_recommendations(budget_min: float, budget_max: float, max_results: int = 10, location: str = None):
    """Generate recommendations from real car data"""
    filtered = [car for car in real_car_data if budget_min <= car['price'] <= budget_max]
    if location:
        location_clean = location.strip().lower()
        filtered = [car for car in filtered if location_clean in car.get('location', '').strip().lower()]
    recommendations = []
    for car in filtered[:max_results]:
        rec = {
            "title": car["title"],
            "year": car["year"],
            "price": car["price"],
            "mileage": car["mileage"],
            "location": car["location"],
            "url": car.get("url", ""),
            "confidence_score": random.uniform(0.7, 0.95),
            "profit_margin": random.uniform(0.1, 0.3),
            "turnover_days": random.randint(15, 60),
            "demand_score": random.uniform(0.5, 0.9)
        }
        recommendations.append(rec)
    return {
        "recommendations": recommendations,
        "total_found": len(filtered),
        "market_summary": {
            "total_inventory": len(filtered),
            "avg_price": sum(r["price"] for r in filtered) / len(filtered) if filtered else 0,
            "price_range": {
                "min": min(r["price"] for r in filtered) if filtered else 0,
                "max": max(r["price"] for r in filtered) if filtered else 0
            }
        }
    }

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wheels Predict API - MVP",
        "version": "1.0.0",
        "status": "active",
        "features": ["Authentication", "Price Prediction", "Recommendations", "Market Analysis"],
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
        "version": "1.0.0",
        "users_loaded": len(users_db)
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
                "name": "ABC Motors",
                "features": ["Price Prediction", "Recommendations", "Market Analysis"]
            },
            {
                "email": "reseller1@example.com",
                "password": "password123",
                "type": "reseller",
                "name": "Quick Cars",
                "features": ["Price Prediction", "Recommendations"]
            },
            {
                "email": "admin@wheelspredict.com",
                "password": "admin123",
                "type": "admin",
                "name": "Admin User",
                "features": ["All Features", "Advanced Analytics"]
            }
        ],
        "note": "Use these credentials to test the MVP API"
    }

@app.post("/auth/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user"""
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user.user_type not in ["dealer", "reseller"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User type must be 'dealer' or 'reseller'"
        )
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    max_calls = 1000 if user.user_type == "dealer" else 500
    
    users_db[user.email] = {
        "email": user.email,
        "hashed_password": hashed_password,
        "user_type": user.user_type,
        "name": user.name,
        "location": user.location,
        "phone": user.phone,
        "verified": True,
        "api_calls": 0,
        "max_api_calls": max_calls,
        "created_at": datetime.utcnow().isoformat()
    }
    
    save_users_db()
    
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
    
    if not bcrypt.checkpw(user.password.encode('utf-8'), user_data["hashed_password"].encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
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

@app.post("/api/predict-price", response_model=PriceResponse)
async def predict_price(request: PriceRequest, current_user: dict = Depends(get_current_user)):
    """Predict car price with enhanced features"""
    check_api_limit(current_user)
    
    try:
        prediction = mock_price_prediction(
            request.make, request.model, request.year, 
            request.mileage, request.engine_capacity
        )
        
        # Add market insights for dealers
        market_insights = None
        if current_user["user_type"] == "dealer":
            market_insights = {
                "demand_score": round(random.uniform(0.6, 0.9), 2),
                "inventory_level": random.choice(["low", "medium", "high"]),
                "price_trend": random.choice(["rising", "stable", "falling"]),
                "regional_demand": f"High demand in {request.location}",
                "best_time_to_sell": random.choice(["Now", "Next Month", "Peak Season"])
            }
        
        increment_api_calls(current_user)
        
        return PriceResponse(
            predicted_price=prediction["predicted_price"],
            confidence=prediction["confidence"],
            price_range=prediction["price_range"],
            model_info=prediction["model_info"],
            market_insights=market_insights
        )
        
    except Exception as e:
        logger.error(f"Price prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/api/dealer-recommendations", response_model=RecommendationResponse)
async def get_dealer_recommendations(request: RecommendationRequest, current_user: dict = Depends(get_current_user)):
    """Get recommendations from real car data"""
    check_api_limit(current_user)
    try:
        # Use location if provided
        location = request.location if hasattr(request, 'location') and request.location else None
        recommendations = real_recommendations(
            request.budget_min, request.budget_max, request.max_results, location
        )
        increment_api_calls(current_user)
        return RecommendationResponse(
            recommendations=recommendations["recommendations"],
            total_found=recommendations["total_found"],
            market_summary=recommendations["market_summary"]
        )
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@app.post("/api/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(request: MarketAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Get market analysis (premium feature for dealers)"""
    check_api_limit(current_user)
    
    if current_user["user_type"] not in ["dealer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Market analysis is only available for dealers"
        )
    
    try:
        market_trends = {
            "price_trend": random.choice(["rising", "stable", "falling"]),
            "volume_trend": random.choice(["increasing", "stable", "decreasing"]),
            "seasonal_factor": round(random.uniform(0.9, 1.1), 2),
            "market_growth": round(random.uniform(0.05, 0.15), 3)
        }
        
        price_analysis = {
            "avg_price": random.randint(2000000, 3000000),
            "price_change_30d": round(random.uniform(-0.05, 0.05), 3),
            "price_volatility": round(random.uniform(0.1, 0.2), 2),
            "value_score": round(random.uniform(0.6, 0.9), 2)
        }
        
        inventory_insights = {
            "total_listings": random.randint(1000, 1500),
            "new_listings_7d": random.randint(30, 60),
            "avg_days_on_market": random.randint(20, 40),
            "turnover_rate": round(random.uniform(0.1, 0.15), 3)
        }
        
        recommendations = [
            "Consider stocking more compact cars for urban areas",
            "SUVs showing strong demand in current market",
            "Automatic transmission vehicles preferred by 70% of buyers",
            "Focus on 2018-2020 model years for best turnover",
            "Hybrid vehicles gaining popularity in major cities"
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
        total_listings = len(real_car_data)
        avg_price = int(sum(car['price'] for car in real_car_data) / total_listings) if total_listings > 0 else 0
        # Optionally, you can compute popular makes and locations from the data
        dashboard_data = {
            "user_stats": {
                "api_calls_today": current_user["api_calls"],
                "remaining_calls": current_user["max_api_calls"] - current_user["api_calls"],
                "usage_percentage": round((current_user["api_calls"] / current_user["max_api_calls"]) * 100, 1)
            },
            "quick_stats": {
                "total_listings": total_listings,
                "avg_price": avg_price,
                "popular_makes": ["Toyota", "Honda", "Suzuki"],
                "locations": ["Karachi", "Lahore", "Islamabad"]
            }
        }
        if current_user["user_type"] == "dealer":
            dashboard_data["dealer_insights"] = {
                "market_opportunities": random.randint(3, 8),
                "trending_models": ["Corolla", "Civic", "Alto"],
                "profit_opportunities": random.randint(2, 5)
            }
        return dashboard_data
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


@app.post("/api/parse-vehicle", response_model=ParseTextResponse)
async def parse_vehicle(req: ParseTextRequest, current_user: dict = Depends(get_current_user)):
    """Parse free text to extract structured vehicle info"""
    check_api_limit(current_user)
    try:
        parsed = parse_text_record(req.text)
        increment_api_calls(current_user)
        return {"parsed": parsed}
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")


@app.post("/api/predict-price-ml", response_model=MLPredictResponse)
async def predict_price_ml(req: MLPredictRequest, current_user: dict = Depends(get_current_user)):
    """Predict price using the trained ML pipeline saved under models/."""
    check_api_limit(current_user)
    if not PriceModel.is_ready():
        raise HTTPException(status_code=503, detail="ML model not available. Train and save a model under models/.")
    try:
        if req.text:
            result = PriceModel.predict_from_text(req.text)
            increment_api_calls(current_user)
            return MLPredictResponse(predicted_price=result['predicted_price'], parsed=result.get('parsed'))
        elif req.features:
            pred = PriceModel.predict_structured(req.features)
            increment_api_calls(current_user)
            return MLPredictResponse(predicted_price=pred['predicted_price'], parsed=None)
        else:
            raise HTTPException(status_code=400, detail="Provide either 'text' or 'features'.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"ML prediction error: {str(e)}")


@app.get("/api/model-status")
async def model_status():
    """Report ML model availability and path."""
    path = PriceModel.load_latest()
    return {"ready": PriceModel.is_ready(), "model_path": path}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load users database and real car data on startup"""
    logger.info("Starting Wheels Predict API - MVP...")
    load_users_db()
    load_real_car_data()
    try:
        path = None
        if 'PriceModel' in globals():
            path = PriceModel.load_latest()
        logger.info(f"ML model ready: {PriceModel.is_ready() if 'PriceModel' in globals() else False} path={path}")
    except Exception as e:
        logger.warning(f"ML model load failed: {e}")
    logger.info(f"Loaded {len(users_db)} users")
    logger.info(f"Loaded {len(real_car_data)} cars from CSV")
    logger.info("Wheels Predict API - MVP startup completed successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
