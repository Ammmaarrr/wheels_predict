"""
Enhanced API Wrapper
Uses enhanced features for better predictions and recommendations
"""

import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import warnings
import sys

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from pakistani_car_variants import get_car_variants, get_car_info, is_valid_variant
    HAS_VARIANT_MAPPING = True
except ImportError:
    HAS_VARIANT_MAPPING = False

warnings.filterwarnings('ignore')

@dataclass
class CarSpecification:
    """Data class for car specifications."""
    make: str
    model: str
    year: int
    engine_capacity: float
    transmission: str
    variant: str = "unknown"
    mileage: Optional[float] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'make': self.make.lower(),
            'model': self.model.lower(),
            'year': self.year,
            'engine_capacity': self.engine_capacity,
            'transmission': self.transmission.lower(),
            'variant': self.variant.lower(),
            'mileage': self.mileage,
            'fuel_type': self.fuel_type.lower() if self.fuel_type else None,
            'body_type': self.body_type.lower() if self.body_type else None,
        }

class EnhancedAPIWrapper:
    """Enhanced API wrapper using new features."""
    
    def __init__(self):
        self.enhanced_data = None
        self.has_variant_mapping = HAS_VARIANT_MAPPING
        self.feature_mappings = {
            'make': ['extracted_make', 'make', 'Make'],
            'model': ['extracted_model', 'model', 'Model'],
            'year': ['extracted_year', 'year', 'Year'],
            'engine_capacity': ['extracted_engine_capacity_cc', 'engine_capacity', 'engineDisplacement'],
            'transmission': ['extracted_transmission_type', 'transmission', 'Transmission'],
            'variant': ['extracted_variant', 'variant', 'Variant'],
            'price': ['extracted_price', 'price', 'Price']
        }
    
    def get_valid_variants(self, make: str, model: str) -> List[str]:
        """Get valid variants for a specific car."""
        if self.has_variant_mapping:
            return get_car_variants(make, model)
        else:
            # Fallback to generic variants
            return ['gli', 'xli', 'vti', 'vxr', 'aspire', 'unknown']
    
    def is_variant_valid(self, make: str, model: str, variant: str) -> bool:
        """Check if a variant is valid for a specific car."""
        if self.has_variant_mapping:
            return is_valid_variant(make, model, variant)
        else:
            # Generic validation
            generic_variants = ['gli', 'xli', 'vti', 'vxr', 'aspire', 'unknown']
            return variant.lower() in [v.lower() for v in generic_variants]
    
    def load_enhanced_data(self):
        """Load enhanced data for predictions."""
        try:
            # Find latest enhanced data
            data_dir = "data/cleaned"
            files = [f for f in os.listdir(data_dir) if f.startswith("cleaned_enhanced") and f.endswith(".csv")]
            
            if files:
                latest_file = sorted(files)[-1]
                data_path = os.path.join(data_dir, latest_file)
                self.enhanced_data = pd.read_csv(data_path, low_memory=False)
                print(f"Enhanced data loaded: {self.enhanced_data.shape}")
                return True
            else:
                print("No enhanced data found")
                return False
                
        except Exception as e:
            print(f"Error loading enhanced data: {e}")
            return False
    
    def get_enhanced_features(self, car_spec: CarSpecification) -> Dict[str, Any]:
        """Get enhanced features for a car using CarSpecification object."""
        
        # Convert to feature dictionary
        features = car_spec.to_dict()
        
        # Add Pakistani market context
        features['is_popular_variant'] = car_spec.variant.lower() in ['vxr', 'gli', 'vx', 'z', 'xli', 'vti']
        features['is_automatic'] = car_spec.transmission.lower() in ['automatic', 'auto', 'cvt']
        features['is_hybrid'] = 'hybrid' in f"{car_spec.make} {car_spec.model} {car_spec.variant}".lower()
        features['is_japanese'] = car_spec.make.lower() in ['toyota', 'honda', 'nissan', 'suzuki', 'daihatsu', 'mitsubishi']
        features['is_recent'] = car_spec.year >= 2018
        features['is_compact'] = car_spec.engine_capacity <= 1000
        features['is_mid_size'] = 1000 < car_spec.engine_capacity <= 1800
        features['is_large'] = car_spec.engine_capacity > 1800
        
        # Calculate car age
        features['car_age'] = 2025 - car_spec.year
        
        # Engine category
        if car_spec.engine_capacity <= 800:
            features['engine_category'] = 'small'
        elif car_spec.engine_capacity <= 1500:
            features['engine_category'] = 'medium'
        elif car_spec.engine_capacity <= 2000:
            features['engine_category'] = 'large'
        else:
            features['engine_category'] = 'extra_large'
        
        return features
    
    def predict_price_enhanced(self, make: str, model: str, year: int, 
                             engine_capacity: float, transmission: str, 
                             variant: str = "unknown", mileage: int = 50000) -> Dict[str, Any]:
        """Enhanced price prediction using new features."""
        
        # Get enhanced features
        features = self.get_enhanced_features(make, model, year, engine_capacity, transmission, variant)
        
        # Base price estimation using enhanced data
        base_price = self._estimate_base_price(features)
        
        # Apply adjustments based on enhanced features
        adjusted_price = self._apply_enhanced_adjustments(base_price, features, mileage)
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(features)
        
        return {
            'predicted_price': adjusted_price,
            'confidence': confidence,
            'price_range': {
                'min': adjusted_price * 0.85,
                'max': adjusted_price * 1.15
            },
            'features_used': features,
            'model_info': {
                'type': 'Enhanced Feature-Based Model',
                'version': '2.0',
                'enhanced_features': True
            }
        }
    
    def _estimate_base_price(self, features: Dict[str, Any]) -> float:
        """Estimate base price using enhanced features."""
        
        # Load enhanced data for price estimation
        if self.enhanced_data is None:
            self.load_enhanced_data()
        
        if self.enhanced_data is not None:
            # Find similar cars in enhanced data
            similar_cars = self.enhanced_data[
                (self.enhanced_data['extracted_make'].str.lower() == features['make']) &
                (self.enhanced_data['extracted_model'].str.lower() == features['model']) &
                (self.enhanced_data['extracted_year'] >= features['year'] - 2) &
                (self.enhanced_data['extracted_year'] <= features['year'] + 2)
            ]
            
            if len(similar_cars) > 0:
                # Use median price of similar cars
                price_col = None
                for col in ['extracted_price', 'price', 'Price']:
                    if col in similar_cars.columns:
                        price_col = col
                        break
                
                if price_col:
                    similar_prices = pd.to_numeric(similar_cars[price_col], errors='coerce').dropna()
                    if len(similar_prices) > 0:
                        base_price = similar_prices.median()
                        print(f"Found {len(similar_prices)} similar cars, median price: {base_price:,.0f}")
                        return base_price
        
        # Fallback to Pakistani market averages
        market_prices = {
            ('toyota', 'corolla'): 3500000,
            ('honda', 'civic'): 4200000,
            ('honda', 'city'): 3800000,
            ('suzuki', 'alto'): 1800000,
            ('suzuki', 'cultus'): 2200000,
            ('suzuki', 'wagon'): 2000000,
            ('suzuki', 'swift'): 2800000,
            ('toyota', 'vitz'): 2500000,
            ('toyota', 'aqua'): 4500000,
            ('toyota', 'prius'): 6000000,
            ('nissan', 'dayz'): 2300000,
            ('kia', 'picanto'): 2800000
        }
        
        key = (features['make'], features['model'])
        base_price = market_prices.get(key, 2500000)  # Default 25 lakh
        
        # Adjust for year
        year_factor = 1 + (features['year'] - 2020) * 0.1
        base_price *= max(0.5, year_factor)
        
        return base_price
    
    def _apply_enhanced_adjustments(self, base_price: float, features: Dict[str, Any], mileage: int) -> float:
        """Apply enhanced feature adjustments."""
        
        adjusted_price = base_price
        
        # Variant adjustments
        if features['is_popular_variant']:
            adjusted_price *= 1.1  # 10% premium for popular variants
        
        # Transmission adjustments
        if features['is_automatic']:
            adjusted_price *= 1.15  # 15% premium for automatic
        
        # Hybrid adjustment
        if features['is_hybrid']:
            adjusted_price *= 1.25  # 25% premium for hybrid
        
        # Japanese brand premium
        if features['is_japanese']:
            adjusted_price *= 1.05  # 5% premium for Japanese brands
        
        # Recent model premium
        if features['is_recent']:
            adjusted_price *= 1.1  # 10% premium for recent models
        
        # Engine size adjustments
        if features['is_compact']:
            adjusted_price *= 0.9  # 10% discount for compact engines
        elif features['is_large']:
            adjusted_price *= 1.15  # 15% premium for large engines
        
        # Age depreciation
        age_factor = max(0.4, 1 - (features['car_age'] * 0.08))  # 8% per year
        adjusted_price *= age_factor
        
        # Mileage adjustment
        if mileage > 100000:
            mileage_factor = max(0.7, 1 - (mileage - 100000) / 1000000)
            adjusted_price *= mileage_factor
        
        return int(adjusted_price)
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate prediction confidence."""
        
        confidence = 0.7  # Base confidence
        
        # Boost confidence for popular models
        if features['make'] in ['toyota', 'honda', 'suzuki']:
            confidence += 0.1
        
        # Boost confidence for popular variants
        if features['is_popular_variant']:
            confidence += 0.05
        
        # Boost confidence for recent models
        if features['is_recent']:
            confidence += 0.1
        
        # Reduce confidence for very old cars
        if features['car_age'] > 10:
            confidence -= 0.1
        
        return min(0.95, max(0.5, confidence))
    
    def get_enhanced_recommendations(self, budget: float, preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get enhanced recommendations."""
        
        if self.enhanced_data is None:
            self.load_enhanced_data()
        
        if self.enhanced_data is None:
            return []
        
        # Filter by budget
        price_col = None
        for col in ['extracted_price', 'price', 'Price']:
            if col in self.enhanced_data.columns:
                price_col = col
                break
        
        if not price_col:
            return []
        
        # Filter data
        filtered_data = self.enhanced_data.copy()
        
        # Convert price to numeric
        filtered_data[price_col] = pd.to_numeric(filtered_data[price_col], errors='coerce')
        
        # Budget filtering with tolerance
        budget_min = budget * 0.8
        budget_max = budget * 1.2
        
        filtered_data = filtered_data[
            (filtered_data[price_col] >= budget_min) &
            (filtered_data[price_col] <= budget_max)
        ].dropna(subset=[price_col])
        
        # Apply preferences
        if preferences:
            for key, value in preferences.items():
                if key == 'transmission' and 'extracted_transmission_type' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['extracted_transmission_type'].str.lower() == value.lower()]
                elif key == 'min_year' and 'extracted_year' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['extracted_year'] >= value]
                elif key == 'make' and 'extracted_make' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['extracted_make'].str.lower() == value.lower()]
        
        # Sort by price and return top recommendations
        recommendations = []
        for _, row in filtered_data.head(10).iterrows():
            rec = {
                'make': row.get('extracted_make', 'Unknown'),
                'model': row.get('extracted_model', 'Unknown'),
                'year': row.get('extracted_year', 2020),
                'price': row.get(price_col, budget),
                'engine_capacity': row.get('extracted_engine_capacity_cc', 1300),
                'transmission': row.get('extracted_transmission_type', 'manual'),
                'variant': row.get('extracted_variant', 'unknown'),
                'match_score': min(1.0, abs(budget - row.get(price_col, budget)) / budget)
            }
            recommendations.append(rec)
        
        return recommendations

# Global instance
enhanced_api = EnhancedAPIWrapper()
enhanced_api.load_enhanced_data()
