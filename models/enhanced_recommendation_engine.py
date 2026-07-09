"""
Enhanced Recommendation Engine
Uses extracted features for better car recommendations
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from typing import List, Dict, Any

class EnhancedRecommendationEngine:
    def __init__(self):
        self.df = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.similarity_matrix = None
        self.feature_matrix = None
        
    def load_enhanced_data(self, data_path: str):
        """Load the enhanced dataset."""
        print(f"Loading enhanced dataset from: {data_path}")
        self.df = pd.read_csv(data_path)
        print(f"Dataset shape: {self.df.shape}")
        
        # Prepare features for recommendations
        self._prepare_recommendation_features()
        
    def _prepare_recommendation_features(self):
        """Prepare features for recommendation engine."""
        print("Preparing recommendation features...")
        
        # Use extracted features with fallback
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
                if col in self.df.columns:
                    self.df[f'rec_{feature_name}'] = self.df[col]
                    break
            else:
                # Create default values
                if feature_name == 'variant':
                    self.df[f'rec_{feature_name}'] = 'unknown'
                elif feature_name == 'transmission':
                    self.df[f'rec_{feature_name}'] = 'unknown'
                else:
                    self.df[f'rec_{feature_name}'] = 0
        
        # Clean data
        self._clean_recommendation_data()
        
        # Create feature matrix
        self._create_feature_matrix()
        
    def _clean_recommendation_data(self):
        """Clean recommendation data."""
        # Clean numeric features
        self.df['rec_year'] = pd.to_numeric(self.df['rec_year'], errors='coerce').fillna(2010)
        self.df['rec_year'] = self.df['rec_year'].clip(1990, 2025)
        
        self.df['rec_engine_capacity'] = pd.to_numeric(self.df['rec_engine_capacity'], errors='coerce').fillna(1000)
        self.df['rec_engine_capacity'] = self.df['rec_engine_capacity'].clip(400, 5000)
        
        self.df['rec_price'] = pd.to_numeric(self.df['rec_price'], errors='coerce').fillna(0)
        
        # Clean categorical features
        self.df['rec_make'] = self.df['rec_make'].fillna('Unknown').astype(str)
        self.df['rec_model'] = self.df['rec_model'].fillna('Unknown').astype(str)
        self.df['rec_transmission'] = self.df['rec_transmission'].fillna('unknown').astype(str)
        self.df['rec_variant'] = self.df['rec_variant'].fillna('unknown').astype(str)
        
        # Filter valid data
        valid_mask = (
            (self.df['rec_price'] > 50000) & 
            (self.df['rec_price'] < 50000000) &
            (self.df['rec_year'] >= 1990) &
            (self.df['rec_year'] <= 2025)
        )
        
        self.df = self.df[valid_mask].reset_index(drop=True)
        print(f"Data cleaned. Valid records: {len(self.df)}")
        
    def _create_feature_matrix(self):
        """Create feature matrix for similarity calculation."""
        print("Creating feature matrix for recommendations...")
        
        # Encode categorical features
        categorical_features = ['rec_make', 'rec_model', 'rec_transmission', 'rec_variant']
        
        for col in categorical_features:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                self.df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(self.df[col])
            else:
                self.df[f'{col}_encoded'] = self.label_encoders[col].transform(self.df[col])
        
        # Create derived features
        self.df['car_age'] = 2025 - self.df['rec_year']
        self.df['price_per_cc'] = self.df['rec_price'] / self.df['rec_engine_capacity']
        
        # Define feature columns for similarity
        feature_columns = [
            'rec_make_encoded', 'rec_model_encoded', 'rec_transmission_encoded',
            'rec_variant_encoded', 'rec_engine_capacity', 'car_age', 'price_per_cc'
        ]
        
        # Create feature matrix
        self.feature_matrix = self.df[feature_columns].values
        
        # Scale features
        self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.feature_matrix)
        
        print("Feature matrix created successfully!")
        
    def get_recommendations(self, 
                          budget: float, 
                          preferences: Dict[str, Any] = None,
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """Get car recommendations based on budget and preferences."""
        
        if self.df is None:
            raise ValueError("Data not loaded. Please load enhanced dataset first.")
        
        print(f"Getting recommendations for budget: {budget:,.0f} PKR")
        
        # Filter by budget (±20% tolerance)
        budget_min = budget * 0.8
        budget_max = budget * 1.2
        
        budget_filtered = self.df[
            (self.df['rec_price'] >= budget_min) & 
            (self.df['rec_price'] <= budget_max)
        ].copy()
        
        if len(budget_filtered) == 0:
            # Expand budget range if no matches
            budget_min = budget * 0.6
            budget_max = budget * 1.4
            budget_filtered = self.df[
                (self.df['rec_price'] >= budget_min) & 
                (self.df['rec_price'] <= budget_max)
            ].copy()
        
        # Apply preference filters
        if preferences:
            budget_filtered = self._apply_preference_filters(budget_filtered, preferences)
        
        if len(budget_filtered) == 0:
            print("No cars found matching criteria. Returning top budget matches.")
            budget_filtered = self.df[
                (self.df['rec_price'] >= budget * 0.5) & 
                (self.df['rec_price'] <= budget * 1.5)
            ].copy()
        
        # Score and rank cars
        budget_filtered = self._score_recommendations(budget_filtered, budget, preferences)
        
        # Sort by score and return top results
        recommendations = budget_filtered.nlargest(max_results, 'recommendation_score')
        
        # Format results
        results = []
        for _, car in recommendations.iterrows():
            result = {
                'make': car['rec_make'],
                'model': car['rec_model'],
                'year': int(car['rec_year']),
                'variant': car['rec_variant'],
                'engine_capacity': int(car['rec_engine_capacity']),
                'transmission': car['rec_transmission'],
                'price': int(car['rec_price']),
                'score': float(car['recommendation_score']),
                'match_reason': car.get('match_reason', 'Budget match')
            }
            results.append(result)
        
        print(f"Found {len(results)} recommendations")
        return results
    
    def _apply_preference_filters(self, df: pd.DataFrame, preferences: Dict[str, Any]) -> pd.DataFrame:
        """Apply user preference filters."""
        filtered_df = df.copy()
        
        # Filter by make
        if preferences.get('make'):
            filtered_df = filtered_df[
                filtered_df['rec_make'].str.lower().str.contains(
                    preferences['make'].lower(), na=False
                )
            ]
        
        # Filter by transmission
        if preferences.get('transmission'):
            filtered_df = filtered_df[
                filtered_df['rec_transmission'].str.lower() == preferences['transmission'].lower()
            ]
        
        # Filter by year range
        if preferences.get('min_year'):
            filtered_df = filtered_df[filtered_df['rec_year'] >= preferences['min_year']]
        
        if preferences.get('max_year'):
            filtered_df = filtered_df[filtered_df['rec_year'] <= preferences['max_year']]
        
        # Filter by engine capacity range
        if preferences.get('min_engine_capacity'):
            filtered_df = filtered_df[
                filtered_df['rec_engine_capacity'] >= preferences['min_engine_capacity']
            ]
        
        if preferences.get('max_engine_capacity'):
            filtered_df = filtered_df[
                filtered_df['rec_engine_capacity'] <= preferences['max_engine_capacity']
            ]
        
        return filtered_df
    
    def _score_recommendations(self, df: pd.DataFrame, budget: float, preferences: Dict[str, Any]) -> pd.DataFrame:
        """Score recommendations based on various factors."""
        df = df.copy()
        
        # Base score
        df['recommendation_score'] = 0.0
        
        # Budget proximity score (higher is better)
        price_diff = abs(df['rec_price'] - budget) / budget
        df['budget_score'] = 1.0 - np.clip(price_diff, 0, 1)
        df['recommendation_score'] += df['budget_score'] * 0.3
        
        # Popularity score (based on make/model frequency)
        make_model_counts = df.groupby(['rec_make', 'rec_model']).size()
        df['popularity_score'] = df.apply(
            lambda row: make_model_counts.get((row['rec_make'], row['rec_model']), 0), 
            axis=1
        )
        df['popularity_score'] = df['popularity_score'] / df['popularity_score'].max()
        df['recommendation_score'] += df['popularity_score'] * 0.2
        
        # Age score (newer cars get higher score)
        df['age_score'] = (df['rec_year'] - df['rec_year'].min()) / (df['rec_year'].max() - df['rec_year'].min())
        df['recommendation_score'] += df['age_score'] * 0.2
        
        # Variant score (known variants get higher score)
        df['variant_score'] = df['rec_variant'].apply(lambda x: 0.8 if x != 'unknown' else 0.2)
        df['recommendation_score'] += df['variant_score'] * 0.1
        
        # Transmission preference score
        if preferences and preferences.get('transmission'):
            df['transmission_score'] = df['rec_transmission'].apply(
                lambda x: 1.0 if x.lower() == preferences['transmission'].lower() else 0.5
            )
            df['recommendation_score'] += df['transmission_score'] * 0.2
        
        # Add match reason
        df['match_reason'] = df.apply(self._get_match_reason, axis=1)
        
        return df
    
    def _get_match_reason(self, row) -> str:
        """Get match reason for a recommendation."""
        reasons = []
        
        if row['budget_score'] > 0.8:
            reasons.append("Perfect budget match")
        elif row['budget_score'] > 0.6:
            reasons.append("Good budget match")
        
        if row['popularity_score'] > 0.7:
            reasons.append("Popular choice")
        
        if row['age_score'] > 0.7:
            reasons.append("Recent model")
        
        if row['rec_variant'] != 'unknown':
            reasons.append(f"Variant: {row['rec_variant']}")
        
        return " | ".join(reasons) if reasons else "Budget match"
    
    def get_similar_cars(self, car_index: int, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get similar cars based on features."""
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not computed. Please load data first.")
        
        # Get similarity scores for the given car
        sim_scores = list(enumerate(self.similarity_matrix[car_index]))
        
        # Sort by similarity score
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top similar cars (excluding the car itself)
        similar_indices = [i for i, _ in sim_scores[1:max_results+1]]
        
        # Format results
        results = []
        for idx in similar_indices:
            car = self.df.iloc[idx]
            result = {
                'make': car['rec_make'],
                'model': car['rec_model'],
                'year': int(car['rec_year']),
                'variant': car['rec_variant'],
                'engine_capacity': int(car['rec_engine_capacity']),
                'transmission': car['rec_transmission'],
                'price': int(car['rec_price']),
                'similarity_score': float(sim_scores[idx][1])
            }
            results.append(result)
        
        return results
    
    def save_recommendation_engine(self, save_path: str):
        """Save the recommendation engine."""
        engine_data = {
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_matrix': self.feature_matrix,
            'similarity_matrix': self.similarity_matrix
        }
        
        # Save the dataframe separately
        self.df.to_csv(save_path.replace('.joblib', '_data.csv'), index=False)
        
        # Save engine components
        joblib.dump(engine_data, save_path)
        print(f"Recommendation engine saved to: {save_path}")
    
    def load_recommendation_engine(self, load_path: str):
        """Load the recommendation engine."""
        # Load engine components
        engine_data = joblib.load(load_path)
        
        self.label_encoders = engine_data['label_encoders']
        self.scaler = engine_data['scaler']
        self.feature_matrix = engine_data['feature_matrix']
        self.similarity_matrix = engine_data['similarity_matrix']
        
        # Load the dataframe
        self.df = pd.read_csv(load_path.replace('.joblib', '_data.csv'))
        
        print(f"Recommendation engine loaded from: {load_path}")

def main():
    """Main function to test the recommendation engine."""
    print("Testing Enhanced Recommendation Engine...")
    print("=" * 60)
    
    # Initialize engine
    engine = EnhancedRecommendationEngine()
    
    # Load enhanced dataset
    data_path = "data/cleaned/cleaned_enhanced_2025-07-11_03-58-18.csv"
    
    try:
        engine.load_enhanced_data(data_path)
    except FileNotFoundError:
        print(f"Enhanced dataset not found at: {data_path}")
        print("Please run the enhanced preprocessing first!")
        return
    
    # Test recommendations
    print("\nTesting recommendations...")
    
    # Test case 1: Budget-based recommendation
    recommendations = engine.get_recommendations(
        budget=2500000,  # 25 lakh
        preferences={
            'transmission': 'automatic',
            'min_year': 2018
        },
        max_results=5
    )
    
    print(f"\nTop 5 recommendations for 25 lakh budget:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['make']} {rec['model']} {rec['year']} - {rec['price']:,} PKR")
        print(f"   Variant: {rec['variant']}, Engine: {rec['engine_capacity']}cc")
        print(f"   Score: {rec['score']:.2f}, Reason: {rec['match_reason']}")
        print()
    
    # Save recommendation engine
    engine.save_recommendation_engine("models/enhanced_recommendation_engine.joblib")
    
    print("Enhanced recommendation engine testing completed!")

if __name__ == "__main__":
    main()
