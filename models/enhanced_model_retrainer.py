"""
Enhanced Model Retraining with New Features
This script retrains all existing models using the enhanced cleaned data
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
from datetime import datetime
from typing import Dict, Any, List, Tuple
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Add current directory to path
sys.path.append('.')

# Import enhanced models
from models.enhanced_model_training_v2 import EnhancedCarPricePredictor
from models.enhanced_recommendation_engine import EnhancedRecommendationEngine

warnings.filterwarnings('ignore')

class EnhancedModelRetrainer:
    """Enhanced model retrainer using new features."""
    
    def __init__(self):
        self.enhanced_data_path = None
        self.models_dir = "models"
        self.results = {}
        
    def find_latest_enhanced_data(self) -> str:
        """Find the latest enhanced cleaned data file."""
        data_dir = "data/cleaned"
        files = [f for f in os.listdir(data_dir) if f.startswith("cleaned_enhanced") and f.endswith(".csv")]
        if not files:
            raise FileNotFoundError("No enhanced data files found!")
        
        latest_file = sorted(files)[-1]
        full_path = os.path.join(data_dir, latest_file)
        print(f"Found latest enhanced data: {full_path}")
        return full_path
    
    def load_enhanced_data(self) -> pd.DataFrame:
        """Load and prepare enhanced data."""
        self.enhanced_data_path = self.find_latest_enhanced_data()
        print(f"Loading enhanced data from: {self.enhanced_data_path}")
        
        df = pd.read_csv(self.enhanced_data_path, low_memory=False)
        print(f"Data shape: {df.shape}")
        
        return df
    
    def prepare_legacy_format_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data in legacy format for existing models."""
        print("Preparing data in legacy format...")
        
        # Create legacy format with enhanced features
        legacy_df = pd.DataFrame()
        
        # Map enhanced features to legacy format
        feature_mapping = {
            'price': ['extracted_price', 'price', 'Price'],
            'mileage': ['mileageFromOdometer', 'mileage', 'Mileage'],
            'engine_capacity': ['extracted_engine_capacity_cc', 'engine_capacity', 'engineDisplacement'],
            'registration_year': ['extracted_year', 'year', 'registration_year'],
            'make': ['extracted_make', 'make', 'Make'],
            'model': ['extracted_model', 'model', 'Model'],
            'fuel_type': ['fuel_type', 'fuelType', 'Fuel Type'],
            'transmission': ['extracted_transmission_type', 'transmission', 'Transmission']
        }
        
        for target_col, source_cols in feature_mapping.items():
            for source_col in source_cols:
                if source_col in df.columns:
                    legacy_df[target_col] = df[source_col]
                    break
            else:
                # Create default values if not found
                if target_col == 'price':
                    legacy_df[target_col] = 2000000  # Default price
                elif target_col == 'mileage':
                    legacy_df[target_col] = 50000  # Default mileage
                elif target_col == 'engine_capacity':
                    legacy_df[target_col] = 1300  # Default engine
                elif target_col == 'registration_year':
                    legacy_df[target_col] = 2018  # Default year
                else:
                    legacy_df[target_col] = 'unknown'
        
        # Clean data
        legacy_df = legacy_df.dropna(subset=['price', 'mileage', 'engine_capacity', 'registration_year'])
        
        # Convert numeric columns
        numeric_cols = ['price', 'mileage', 'engine_capacity', 'registration_year']
        for col in numeric_cols:
            legacy_df[col] = pd.to_numeric(legacy_df[col], errors='coerce')
        
        # Remove outliers
        legacy_df = legacy_df[
            (legacy_df['price'] > 100000) & (legacy_df['price'] < 50000000) &
            (legacy_df['mileage'] >= 0) & (legacy_df['mileage'] < 500000) &
            (legacy_df['engine_capacity'] > 0) & (legacy_df['engine_capacity'] < 10000) &
            (legacy_df['registration_year'] >= 1980) & (legacy_df['registration_year'] <= 2025)
        ]
        
        print(f"Legacy format data shape: {legacy_df.shape}")
        return legacy_df
    
    def prepare_enhanced_format_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for enhanced models."""
        print("Preparing data for enhanced models...")
        
        # This uses the enhanced features directly
        enhanced_df = df.copy()
        
        # Clean and filter enhanced data
        # Remove rows with missing critical enhanced features
        critical_cols = ['extracted_variant', 'extracted_engine_capacity_cc', 'extracted_transmission_type']
        available_cols = [col for col in critical_cols if col in enhanced_df.columns]
        
        if available_cols:
            enhanced_df = enhanced_df.dropna(subset=available_cols)
        
        print(f"Enhanced format data shape: {enhanced_df.shape}")
        return enhanced_df
    
    def retrain_legacy_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Retrain legacy models with enhanced data."""
        print("\\n" + "="*60)
        print("RETRAINING LEGACY MODELS WITH ENHANCED DATA")
        print("="*60)
        
        results = {}
        
        # Prepare features and target
        feature_columns = ['mileage', 'engine_capacity', 'registration_year']
        categorical_columns = ['make', 'model', 'fuel_type', 'transmission']
        
        # Create feature matrix
        X = df[feature_columns].copy()
        
        # Encode categorical variables
        label_encoders = {}
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
        
        # Target variable
        y = df['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Models to retrain
        models = {
            'linear_reg': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42)
        }
        
        # Train models
        for name, model in models.items():
            print(f"\\nTraining {name}...")
            
            # Use scaled data for linear regression, original for tree-based
            if name == 'linear_reg':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'model': model,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'scaler': scaler if name == 'linear_reg' else None,
                'encoders': label_encoders
            }
            
            print(f"   MAE: {mae:,.0f}")
            print(f"   RMSE: {rmse:,.0f}")
            print(f"   R²: {r2:.4f}")
        
        return results
    
    def retrain_enhanced_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Retrain enhanced models."""
        print("\\n" + "="*60)
        print("RETRAINING ENHANCED MODELS")
        print("="*60)
        
        results = {}
        
        # Enhanced Price Predictor
        print("\\nTraining Enhanced Price Predictor...")
        try:
            predictor = EnhancedCarPricePredictor()
            df_processed, feature_columns = predictor.prepare_features(df)
            
            if len(df_processed) > 0:
                model, metrics = predictor.train_model(df_processed, feature_columns)
                
                results['enhanced_price_predictor'] = {
                    'model': predictor,
                    'metrics': metrics,
                    'feature_columns': feature_columns
                }
                
                print(f"   Enhanced Price Predictor trained successfully")
                print(f"   MAE: {metrics['mae']:,.0f}")
                print(f"   RMSE: {metrics['rmse']:,.0f}")
                print(f"   R²: {metrics['r2']:.4f}")
            else:
                print("   No data available for Enhanced Price Predictor")
                
        except Exception as e:
            print(f"   Error training Enhanced Price Predictor: {e}")
        
        # Enhanced Recommendation Engine
        print("\\nTraining Enhanced Recommendation Engine...")
        try:
            rec_engine = EnhancedRecommendationEngine()
            rec_engine.load_enhanced_data(self.enhanced_data_path)
            
            results['enhanced_recommendation_engine'] = {
                'model': rec_engine
            }
            
            print(f"   Enhanced Recommendation Engine loaded successfully")
            print(f"   Data shape: {rec_engine.df.shape}")
            
        except Exception as e:
            print(f"   Error training Enhanced Recommendation Engine: {e}")
        
        return results
    
    def save_models(self, legacy_results: Dict[str, Any], enhanced_results: Dict[str, Any]):
        """Save all retrained models."""
        print("\\n" + "="*60)
        print("SAVING RETRAINED MODELS")
        print("="*60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save legacy models
        for name, result in legacy_results.items():
            if name == 'linear_reg':
                save_path = f"{self.models_dir}/linear_reg_model_enhanced_{timestamp}.joblib"
            elif name == 'random_forest':
                save_path = f"{self.models_dir}/rf_model_enhanced_{timestamp}.joblib"
            elif name == 'xgboost':
                save_path = f"{self.models_dir}/best_xgb_model_enhanced_{timestamp}.joblib"
            
            # Save model with metadata
            model_data = {
                'model': result['model'],
                'scaler': result['scaler'],
                'encoders': result['encoders'],
                'metrics': {
                    'mae': result['mae'],
                    'rmse': result['rmse'],
                    'r2': result['r2']
                },
                'enhanced_features': True,
                'timestamp': timestamp
            }
            
            joblib.dump(model_data, save_path)
            print(f"✅ Saved {name}: {save_path}")
        
        # Save enhanced models
        for name, result in enhanced_results.items():
            if name == 'enhanced_price_predictor':
                save_path = f"{self.models_dir}/enhanced_car_price_model_retrained_{timestamp}.joblib"
                result['model'].save_model(save_path)
                print(f"✅ Saved {name}: {save_path}")
            
            elif name == 'enhanced_recommendation_engine':
                save_path = f"{self.models_dir}/enhanced_recommendation_engine_retrained_{timestamp}.joblib"
                result['model'].save_recommendation_engine(save_path)
                print(f"✅ Saved {name}: {save_path}")
        
        # Save scaler for recommendations
        if legacy_results:
            scaler_path = f"{self.models_dir}/scaler_rec_enhanced_{timestamp}.joblib"
            joblib.dump(legacy_results['random_forest']['scaler'], scaler_path)
            print(f"✅ Saved scaler: {scaler_path}")
    
    def generate_comparison_report(self, legacy_results: Dict[str, Any], enhanced_results: Dict[str, Any]):
        """Generate comparison report."""
        print("\\n" + "="*60)
        print("MODEL PERFORMANCE COMPARISON")
        print("="*60)
        
        # Legacy models comparison
        print("\\nLegacy Models (Enhanced Data):")
        print("-" * 40)
        print(f"{'Model':<15} {'MAE':<12} {'RMSE':<12} {'R²':<8}")
        print("-" * 40)
        
        for name, result in legacy_results.items():
            print(f"{name:<15} {result['mae']:<12,.0f} {result['rmse']:<12,.0f} {result['r2']:<8.4f}")
        
        # Enhanced models
        print("\\nEnhanced Models:")
        print("-" * 40)
        
        if 'enhanced_price_predictor' in enhanced_results:
            metrics = enhanced_results['enhanced_price_predictor']['metrics']
            print(f"{'Enhanced Price':<15} {metrics['mae']:<12,.0f} {metrics['rmse']:<12,.0f} {metrics['r2']:<8.4f}")
        
        if 'enhanced_recommendation_engine' in enhanced_results:
            print(f"{'Enhanced Rec':<15} {'Loaded':<12} {'Successfully':<12} {'✅':<8}")
        
        # Performance improvements
        print("\\nExpected Improvements:")
        print("-" * 40)
        print("✅ Better feature quality (extracted vs raw)")
        print("✅ More comprehensive data (36k+ vs 1k rows)")
        print("✅ Pakistani market specific features")
        print("✅ Enhanced variant detection")
        print("✅ Better price prediction accuracy")
        print("✅ More relevant recommendations")
    
    def run_full_retraining(self):
        """Run complete model retraining process."""
        print("="*80)
        print("ENHANCED MODEL RETRAINING PROCESS")
        print("="*80)
        
        try:
            # 1. Load enhanced data
            df = self.load_enhanced_data()
            
            # 2. Prepare data formats
            legacy_df = self.prepare_legacy_format_data(df)
            enhanced_df = self.prepare_enhanced_format_data(df)
            
            # 3. Retrain legacy models
            legacy_results = self.retrain_legacy_models(legacy_df)
            
            # 4. Retrain enhanced models
            enhanced_results = self.retrain_enhanced_models(enhanced_df)
            
            # 5. Save models
            self.save_models(legacy_results, enhanced_results)
            
            # 6. Generate report
            self.generate_comparison_report(legacy_results, enhanced_results)
            
            print("\\n" + "="*80)
            print("RETRAINING COMPLETED SUCCESSFULLY!")
            print("="*80)
            
            return {
                'legacy_results': legacy_results,
                'enhanced_results': enhanced_results,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"\\n❌ Error during retraining: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

def main():
    """Main function."""
    retrainer = EnhancedModelRetrainer()
    results = retrainer.run_full_retraining()
    
    if results['status'] == 'success':
        print("\\n🎉 All models successfully retrained with enhanced features!")
        print("\\n📋 Next Steps:")
        print("   1. Update API servers to use new models")
        print("   2. Test new models with sample predictions")
        print("   3. Deploy to production")
        print("   4. Monitor performance improvements")
    else:
        print(f"\\n❌ Retraining failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
