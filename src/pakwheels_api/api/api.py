# FastAPI REST API for Car Price Prediction and Recommendation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd
import numpy as np
import os
from database.db_utils import save_predictions_postgres, save_recommendations_mongo
from models.recommendation_engine import enhanced_hybrid_recommendation

# Load models and scaler
BEST_XGB_MODEL_PATH = 'models/best_xgb_model_updated.joblib'
LINEAR_REG_MODEL_PATH = 'models/linear_reg_model_updated.joblib'
RF_MODEL_PATH = 'models/rf_model_updated.joblib'
SCALER_REC_PATH = 'models/scaler_rec_updated.joblib'
CLEANED_DATA_SAVE_PATH = 'data_processing/cleaned_data_for_deployment_updated.csv'

app = FastAPI(title="Car Price Prediction & Recommendation API")

# Load assets at startup
@app.on_event("startup")
def load_assets():
    global xgb_model, linear_model, rf_model, rec_scaler, df_cleaned
    xgb_model = joblib.load(BEST_XGB_MODEL_PATH)
    linear_model = joblib.load(LINEAR_REG_MODEL_PATH)
    rf_model = joblib.load(RF_MODEL_PATH)
    rec_scaler = joblib.load(SCALER_REC_PATH)
    df_cleaned = pd.read_csv(CLEANED_DATA_SAVE_PATH)

# Input schemas
class PriceInput(BaseModel):
    mileageFromOdometer: float
    engineDisplacement: float
    fuelType: str
    seller_location: str
    model: Optional[str] = None
    save_to_db: Optional[bool] = False  # New flag

class RecommendInput(BaseModel):
    car_id: Optional[int] = None
    user_history: Optional[List[str]] = None
    top_n: int = 5
    save_to_db: Optional[bool] = False  # New flag

@app.post("/predict-price")
def predict_price(input: PriceInput):
    try:
        features = ['mileageFromOdometer', 'engineDisplacement', 'fuelType', 'seller_location']
        X = pd.DataFrame([{f: getattr(input, f, None) for f in features}])
        cat_features = ['fuelType', 'seller_location']
        encoder = joblib.load('encoder.joblib') if os.path.exists('encoder.joblib') else None
        if encoder:
            X_cat = encoder.transform(X[cat_features])
            X_cat_df = pd.DataFrame(X_cat, columns=encoder.get_feature_names_out(cat_features))
            X_num = X[['mileageFromOdometer', 'engineDisplacement']]
            X_full = pd.concat([X_num, X_cat_df], axis=1)
        else:
            X_full = X[['mileageFromOdometer', 'engineDisplacement']]
        scaler = joblib.load('scaler.joblib') if os.path.exists('scaler.joblib') else None
        if scaler:
            X_scaled = scaler.transform(X_full)
        else:
            X_scaled = X_full.values
        pred_xgb = float(xgb_model.predict(X_scaled)[0])
        pred_rf = float(rf_model.predict(X_scaled)[0])
        pred_linear = float(linear_model.predict(X_scaled)[0])
        result = {"xgboost": pred_xgb, "random_forest": pred_rf, "linear_regression": pred_linear}
        # Save to PostgreSQL if requested
        if input.save_to_db:
            df_pred = pd.DataFrame([{
                "model": input.model or "Unknown",
                "predicted_price": pred_xgb
            }])
            db_params = {
                "host": "localhost", "dbname": "your_db", "user": "your_user", "password": "your_pass", "port": 5432
            }
            save_predictions_postgres(df_pred, db_params=db_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recommend-cars")
def recommend_cars(input: RecommendInput):
    try:
        if input.car_id is not None:
            car_row = df_cleaned.iloc[[input.car_id]]
            user_history = [car_row['model'].values[0]] if 'model' in car_row.columns else None
        else:
            user_history = input.user_history
        recs = enhanced_hybrid_recommendation(df_cleaned, user_history=user_history, top_n=input.top_n)
        # Save to MongoDB if requested
        if input.save_to_db:
            save_recommendations_mongo(recs)
        return {"recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-insights")
def get_insights():
    try:
        # Example: return price stats and top models
        stats = {
            "price_min": float(df_cleaned['price'].min()),
            "price_max": float(df_cleaned['price'].max()),
            "price_mean": float(df_cleaned['price'].mean()),
            "top_models": df_cleaned['model'].value_counts().head(5).to_dict() if 'model' in df_cleaned.columns else {}
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# To run: uvicorn api:app --reload
