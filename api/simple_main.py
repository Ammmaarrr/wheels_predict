from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI(
    title="PakWheels Simple API",
    description="Simplified API for car price prediction and recommendations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data models
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

class HealthResponse(BaseModel):
    status: str
    message: str

# Sample endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    return {"status": "healthy", "message": "PakWheels API is running"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "healthy", "message": "API is operational"}

@app.post("/predict", response_model=PriceResponse)
async def predict_price(request: PriceRequest):
    # Simple prediction logic (mock)
    base_price = 1500000  # Base price in PKR
    
    # Simple price calculation based on inputs
    year_factor = (request.year - 2000) * 50000
    mileage_factor = -request.mileage * 2
    engine_factor = request.engine_capacity * 100000
    
    predicted_price = base_price + year_factor + mileage_factor + engine_factor
    
    return {
        "predicted_price": max(predicted_price, 200000),  # Minimum price
        "confidence": 0.85,
        "message": "Price prediction completed successfully"
    }

@app.get("/recommendations")
async def get_recommendations():
    # Mock recommendations
    return {
        "recommendations": [
            {"make": "Toyota", "model": "Corolla", "year": 2020, "price": 2500000},
            {"make": "Honda", "model": "Civic", "year": 2019, "price": 2800000},
            {"make": "Suzuki", "model": "Alto", "year": 2021, "price": 1800000}
        ],
        "message": "Recommendations retrieved successfully"
    }

@app.get("/monitoring")
async def get_monitoring():
    return {
        "metrics": {
            "total_predictions": 1247,
            "accuracy": 87.5,
            "system_health": "healthy",
            "active_models": 3
        },
        "status": "operational"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
