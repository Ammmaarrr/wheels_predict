"""
Enhanced ML Model Training with New Features
Uses the enhanced dataset with extracted features for better predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedCarPricePredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def load_enhanced_data(self, data_path):
        """Load the enhanced dataset with extracted features."""
        print(f"Loading enhanced dataset from: {data_path}")
        df = pd.read_csv(data_path)
        print(f"Dataset shape: {df.shape}")
        return df
    
    def prepare_features(self, df):
        """Prepare features for model training using enhanced extracted features."""
        print("Preparing enhanced features...")
        
        # Create a copy for processing
        df_processed = df.copy()
        
        # Use extracted features with fallback to original columns
        feature_mapping = {
            'make': ['extracted_make', 'make', 'Make'],
            'model': ['extracted_model', 'model', 'Model'],
            'year': ['extracted_year', 'year', 'Year'],
            'engine_capacity': ['extracted_engine_capacity_cc', 'engine_capacity', 'Engine Capacity'],
            'transmission': ['extracted_transmission_type', 'transmission', 'Transmission'],
            'variant': ['extracted_variant', 'variant', 'Variant'],
            'price': ['extracted_price', 'price', 'Price']
        }
        
        # Map features using priority order
        for feature_name, possible_columns in feature_mapping.items():
            for col in possible_columns:
                if col in df_processed.columns:
                    df_processed[f'final_{feature_name}'] = df_processed[col]
                    break
            else:
                # If no column found, create default
                if feature_name == 'variant':
                    df_processed[f'final_{feature_name}'] = 'unknown'
                else:
                    df_processed[f'final_{feature_name}'] = 0
        
        # Clean and process features
        df_processed = self._clean_features(df_processed)
        
        # Select features for training
        feature_columns = [
            'final_make', 'final_model', 'final_year', 'final_engine_capacity',
            'final_transmission', 'final_variant'
        ]
        
        # Add derived features
        df_processed['car_age'] = 2025 - df_processed['final_year']
        df_processed['engine_size_category'] = pd.cut(
            df_processed['final_engine_capacity'], 
            bins=[0, 800, 1200, 1600, 2000, 5000], 
            labels=['Small', 'Compact', 'Medium', 'Large', 'XLarge']
        )
        
        feature_columns.extend(['car_age', 'engine_size_category'])
        
        # Filter valid price data
        valid_price_mask = (
            (df_processed['final_price'] > 50000) & 
            (df_processed['final_price'] < 50000000) &
            (df_processed['final_year'] >= 1990) &
            (df_processed['final_year'] <= 2025)
        )
        
        df_processed = df_processed[valid_price_mask]
        
        print(f"Features prepared. Dataset shape after cleaning: {df_processed.shape}")
        print(f"Feature columns: {feature_columns}")
        
        return df_processed, feature_columns
    
    def _clean_features(self, df):
        """Clean and standardize features."""
        # Clean year
        df['final_year'] = pd.to_numeric(df['final_year'], errors='coerce').fillna(2010)
        df['final_year'] = df['final_year'].clip(1990, 2025)
        
        # Clean engine capacity
        df['final_engine_capacity'] = pd.to_numeric(df['final_engine_capacity'], errors='coerce').fillna(1000)
        df['final_engine_capacity'] = df['final_engine_capacity'].clip(400, 5000)
        
        # Clean price
        df['final_price'] = pd.to_numeric(df['final_price'], errors='coerce').fillna(0)
        
        # Clean categorical features
        df['final_make'] = df['final_make'].fillna('Unknown').astype(str)
        df['final_model'] = df['final_model'].fillna('Unknown').astype(str)
        df['final_transmission'] = df['final_transmission'].fillna('unknown').astype(str)
        df['final_variant'] = df['final_variant'].fillna('unknown').astype(str)
        
        return df
    
    def encode_categorical_features(self, df, feature_columns):
        """Encode categorical features."""
        print("Encoding categorical features...")
        
        df_encoded = df.copy()
        categorical_columns = ['final_make', 'final_model', 'final_transmission', 'final_variant', 'engine_size_category']
        
        for col in categorical_columns:
            if col in df_encoded.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(df_encoded[col].astype(str))
                else:
                    df_encoded[col] = self.label_encoders[col].transform(df_encoded[col].astype(str))
        
        return df_encoded
    
    def train_model(self, df, feature_columns, target_column='final_price'):
        """Train the enhanced model."""
        print("Training enhanced model...")
        
        # Encode categorical features
        df_encoded = self.encode_categorical_features(df, feature_columns)
        
        # Prepare features and target
        X = df_encoded[feature_columns]
        y = df_encoded[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models and choose the best
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = float('inf')
        
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"{name} - MAE: {mae:.2f}, MSE: {mse:.2f}, R²: {r2:.4f}")
            
            if mae < best_score:
                best_score = mae
                best_model = model
                self.model = model
        
        self.feature_columns = feature_columns
        
        print(f"Best model selected with MAE: {best_score:.2f}")
        return best_model, best_score
    
    def predict_price(self, make, model, year, engine_capacity, transmission, variant='unknown'):
        """Predict price for a single car."""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Create input dataframe
        input_data = pd.DataFrame({
            'final_make': [make],
            'final_model': [model],
            'final_year': [year],
            'final_engine_capacity': [engine_capacity],
            'final_transmission': [transmission],
            'final_variant': [variant],
            'car_age': [2025 - year],
            'engine_size_category': [self._categorize_engine_size(engine_capacity)]
        })
        
        # Encode categorical features
        input_encoded = self.encode_categorical_features(input_data, self.feature_columns)
        
        # Scale features
        input_scaled = self.scaler.transform(input_encoded[self.feature_columns])
        
        # Predict
        prediction = self.model.predict(input_scaled)[0]
        
        return max(prediction, 50000)  # Minimum price threshold
    
    def _categorize_engine_size(self, engine_capacity):
        """Categorize engine size."""
        if engine_capacity <= 800:
            return 'Small'
        elif engine_capacity <= 1200:
            return 'Compact'
        elif engine_capacity <= 1600:
            return 'Medium'
        elif engine_capacity <= 2000:
            return 'Large'
        else:
            return 'XLarge'
    
    def save_model(self, model_path):
        """Save the trained model and encoders."""
        print(f"Saving model to: {model_path}")
        
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, model_path)
        print("Model saved successfully!")
    
    def load_model(self, model_path):
        """Load a trained model and encoders."""
        print(f"Loading model from: {model_path}")
        
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        
        print("Model loaded successfully!")

def main():
    """Main training function."""
    print("Starting Enhanced Model Training...")
    print("=" * 60)
    
    # Initialize predictor
    predictor = EnhancedCarPricePredictor()
    
    # Load enhanced dataset
    data_path = "data/cleaned/cleaned_enhanced_2025-07-11_03-58-18.csv"
    
    try:
        df = predictor.load_enhanced_data(data_path)
    except FileNotFoundError:
        print(f"Enhanced dataset not found at: {data_path}")
        print("Please run the enhanced preprocessing first!")
        return
    
    # Prepare features
    df_processed, feature_columns = predictor.prepare_features(df)
    
    # Train model
    model, score = predictor.train_model(df_processed, feature_columns)
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"models/enhanced_car_price_model_{timestamp}.joblib"
    predictor.save_model(model_path)
    
    # Test prediction
    print("\nTesting prediction...")
    try:
        test_price = predictor.predict_price(
            make='Toyota',
            model='Corolla',
            year=2020,
            engine_capacity=1300,
            transmission='automatic',
            variant='xli'
        )
        print(f"Test prediction (Toyota Corolla 2020 XLI): {test_price:,.0f} PKR")
    except Exception as e:
        print(f"Test prediction failed: {e}")
    
    print("\nEnhanced model training completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
