"""
Enhanced Model Training Script
Uses the enhanced features from the preprocessing pipeline
"""

import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')

# Directories
CLEANED_DIR = "data/cleaned"
MODELS_DIR = "models"
PREPROCESSORS_DIR = "models/preprocessors"

# Ensure directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PREPROCESSORS_DIR, exist_ok=True)

def get_latest_enhanced_csv():
    """Get the latest enhanced cleaned CSV file."""
    files = [f for f in os.listdir(CLEANED_DIR) if f.startswith('cleaned_enhanced_') and f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No enhanced cleaned CSV files found. Please run the preprocessing script first.")
    files.sort(reverse=True)
    return os.path.join(CLEANED_DIR, files[0])

def prepare_enhanced_data(df):
    """Prepare data using enhanced features."""
    print("Preparing enhanced dataset...")
    
    # Create a copy to work with
    df_prep = df.copy()
    
    # Define enhanced features to use
    enhanced_features = [
        'extracted_variant',
        'extracted_engine_capacity_cc',
        'extracted_transmission_type',
        'extracted_make',
        'extracted_model',
        'extracted_year'
    ]
    
    # Original features that might be useful
    original_features = [
        'year',
        'mileage',
        'engineDisplacement',
        'mileageFromOdometer',
        'color',
        'seller_location',
        'fuelType',
        'bodyType',
        'assembly',
        'transmission'
    ]
    
    # Target variable - try different price columns
    target_col = None
    price_columns = ['price', 'extracted_price', 'priceAmount']
    
    for col in price_columns:
        if col in df_prep.columns:
            # Clean price data
            df_prep[col] = pd.to_numeric(df_prep[col], errors='coerce')
            df_prep = df_prep.dropna(subset=[col])
            
            # Filter reasonable price range (100k to 50M PKR)
            df_prep = df_prep[(df_prep[col] >= 100000) & (df_prep[col] <= 50000000)]
            
            if len(df_prep) > 0:
                target_col = col
                break
    
    if target_col is None:
        raise ValueError("No valid price column found in the dataset")
    
    print(f"Using '{target_col}' as target variable")
    print(f"Dataset shape after price filtering: {df_prep.shape}")
    
    # Prepare features
    features_to_use = []
    
    # Add enhanced features
    for feature in enhanced_features:
        if feature in df_prep.columns:
            features_to_use.append(feature)
    
    # Add original features
    for feature in original_features:
        if feature in df_prep.columns:
            features_to_use.append(feature)
    
    # Remove duplicates
    features_to_use = list(set(features_to_use))
    
    print(f"Features to use: {features_to_use}")
    
    # Create feature matrix
    X = df_prep[features_to_use].copy()
    y = df_prep[target_col].copy()
    
    # Handle missing values and data types
    # Numeric features
    numeric_features = [
        'extracted_engine_capacity_cc',
        'extracted_year',
        'year',
        'mileage',
        'engineDisplacement',
        'mileageFromOdometer'
    ]
    
    # Categorical features
    categorical_features = [
        'extracted_variant',
        'extracted_transmission_type',
        'extracted_make',
        'extracted_model',
        'color',
        'seller_location',
        'fuelType',
        'bodyType',
        'assembly',
        'transmission'
    ]
    
    # Process numeric features
    for feature in numeric_features:
        if feature in X.columns:
            X[feature] = pd.to_numeric(X[feature], errors='coerce')
            X[feature] = X[feature].fillna(X[feature].median())
    
    # Process categorical features
    for feature in categorical_features:
        if feature in X.columns:
            X[feature] = X[feature].astype(str)
            X[feature] = X[feature].fillna('unknown')
    
    print(f"Final feature matrix shape: {X.shape}")
    print(f"Target variable shape: {y.shape}")
    
    return X, y, features_to_use

def create_preprocessing_pipeline(X, categorical_features, numeric_features):
    """Create preprocessing pipeline with proper encoding."""
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    
    # Identify which features are actually present
    present_categorical = [f for f in categorical_features if f in X.columns]
    present_numeric = [f for f in numeric_features if f in X.columns]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), present_numeric),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), present_categorical)
        ]
    )
    
    return preprocessor, present_categorical, present_numeric

def train_enhanced_models(X, y):
    """Train multiple models with enhanced features."""
    print("Training enhanced models...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )
    
    print(f"Training set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    
    # Identify feature types
    numeric_features = [
        'extracted_engine_capacity_cc',
        'extracted_year',
        'year',
        'mileage',
        'engineDisplacement',
        'mileageFromOdometer'
    ]
    
    categorical_features = [
        'extracted_variant',
        'extracted_transmission_type',
        'extracted_make',
        'extracted_model',
        'color',
        'seller_location',
        'fuelType',
        'bodyType',
        'assembly',
        'transmission'
    ]
    
    # Create preprocessing pipeline
    preprocessor, present_categorical, present_numeric = create_preprocessing_pipeline(
        X_train, categorical_features, numeric_features
    )
    
    # Save preprocessing info
    preprocessing_info = {
        'preprocessor': preprocessor,
        'numeric_features': present_numeric,
        'categorical_features': present_categorical,
        'all_features': list(X.columns)
    }
    
    # Define models to train
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Create pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = pipeline.predict(X_train)
        y_pred_test = pipeline.predict(X_test)
        
        # Calculate metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='r2')
        
        results[name] = {
            'model': pipeline,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_mae': test_mae,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
        
        print(f"  Train RMSE: {train_rmse:,.0f}")
        print(f"  Test RMSE: {test_rmse:,.0f}")
        print(f"  Test R²: {test_r2:.4f}")
        print(f"  Test MAE: {test_mae:,.0f}")
        print(f"  CV R² (mean±std): {cv_scores.mean():.4f}±{cv_scores.std():.4f}")
    
    return results, preprocessing_info

def save_best_model(results, preprocessing_info):
    """Save the best performing model."""
    print("\nModel Performance Summary:")
    print("=" * 60)
    
    best_model_name = None
    best_score = -np.inf
    
    for name, result in results.items():
        print(f"{name}:")
        print(f"  Test R²: {result['test_r2']:.4f}")
        print(f"  Test RMSE: {result['test_rmse']:,.0f}")
        print(f"  CV R² (mean±std): {result['cv_r2_mean']:.4f}±{result['cv_r2_std']:.4f}")
        
        # Use CV R² for model selection
        if result['cv_r2_mean'] > best_score:
            best_score = result['cv_r2_mean']
            best_model_name = name
    
    print(f"\nBest model: {best_model_name} (CV R² = {best_score:.4f})")
    
    # Save best model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"enhanced_model_{best_model_name.lower()}_{timestamp}.joblib"
    model_path = os.path.join(MODELS_DIR, model_filename)
    
    joblib.dump(results[best_model_name]['model'], model_path)
    print(f"Best model saved to: {model_path}")
    
    # Save preprocessing info
    preprocessor_filename = f"enhanced_preprocessor_{timestamp}.joblib"
    preprocessor_path = os.path.join(PREPROCESSORS_DIR, preprocessor_filename)
    
    joblib.dump(preprocessing_info, preprocessor_path)
    print(f"Preprocessing info saved to: {preprocessor_path}")
    
    # Save model info
    model_info = {
        'best_model_name': best_model_name,
        'model_path': model_path,
        'preprocessor_path': preprocessor_path,
        'timestamp': timestamp,
        'performance': results[best_model_name],
        'all_results': {k: {
            'test_r2': v['test_r2'],
            'test_rmse': v['test_rmse'],
            'cv_r2_mean': v['cv_r2_mean']
        } for k, v in results.items()}
    }
    
    info_filename = f"enhanced_model_info_{timestamp}.json"
    info_path = os.path.join(MODELS_DIR, info_filename)
    
    import json
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2, default=str)
    
    print(f"Model info saved to: {info_path}")
    
    return model_path, preprocessor_path, model_info

def main():
    """Main training function."""
    print("Enhanced Model Training Pipeline")
    print("=" * 60)
    
    try:
        # Load enhanced data
        data_path = get_latest_enhanced_csv()
        print(f"Loading data from: {data_path}")
        
        df = pd.read_csv(data_path)
        print(f"Original dataset shape: {df.shape}")
        
        # Prepare data
        X, y, features_used = prepare_enhanced_data(df)
        
        # Train models
        results, preprocessing_info = train_enhanced_models(X, y)
        
        # Save best model
        model_path, preprocessor_path, model_info = save_best_model(results, preprocessing_info)
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
        print(f"✅ Best model: {model_info['best_model_name']}")
        print(f"✅ Model saved to: {model_path}")
        print(f"✅ Preprocessor saved to: {preprocessor_path}")
        print(f"✅ Features used: {len(features_used)}")
        
        return model_path, preprocessor_path, model_info
        
    except Exception as e:
        print(f"Error during training: {e}")
        raise

if __name__ == "__main__":
    main()
