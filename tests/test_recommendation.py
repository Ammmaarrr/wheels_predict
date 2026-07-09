import pytest
import pandas as pd
import numpy as np
from models.recommendation_engine import get_similar_cars, preprocess_features, calculate_similarity

def test_feature_preprocessing():
    """Test feature preprocessing for recommendations."""
    # Sample input
    sample_data = pd.DataFrame({
        'year': [2018, 2020],
        'price': [2500000, 3400000],
        'mileage': [45000, 12000],
        'engine_capacity': [1300, 1800],
        'transmission': ['Manual', 'Automatic']
    })
    
    # Process features
    processed_features = preprocess_features(sample_data)
    
    # Check scaling
    assert processed_features.min().min() >= -1
    assert processed_features.max().max() <= 1
    
    # Check expected columns
    expected_features = [
        'year', 'price', 'mileage', 'engine_capacity',
        'transmission_Automatic', 'transmission_Manual'
    ]
    assert all(col in processed_features.columns for col in expected_features)

def test_similarity_calculation():
    """Test similarity calculation between cars."""
    # Sample processed features
    features = np.array([
        [0.5, 0.3, 0.2, 0.1, 1, 0],
        [0.4, 0.3, 0.2, 0.1, 0, 1],
        [0.1, 0.8, 0.9, 0.7, 1, 0]
    ])
    
    # Calculate similarity
    similarity_matrix = calculate_similarity(features)
    
    # Check similarity matrix properties
    assert similarity_matrix.shape == (3, 3)  # Square matrix
    assert np.allclose(similarity_matrix, similarity_matrix.T)  # Symmetry
    assert np.allclose(np.diag(similarity_matrix), 1)  # Self-similarity = 1
    assert (similarity_matrix >= -1).all() and (similarity_matrix <= 1).all()  # Valid range

def test_get_similar_cars(sample_cleaned_data):
    """Test getting similar car recommendations."""
    # Get recommendations
    n_recommendations = 2
    similar_cars = get_similar_cars(
        sample_cleaned_data.iloc[0],  # Reference car
        sample_cleaned_data,
        n_recommendations
    )
    
    # Check number of recommendations
    assert len(similar_cars) == n_recommendations
    
    # Check recommendation properties
    assert isinstance(similar_cars, pd.DataFrame)
    assert 'similarity_score' in similar_cars.columns
    assert (similar_cars['similarity_score'] >= -1).all()
    assert (similar_cars['similarity_score'] <= 1).all()

def test_recommendation_edge_cases(sample_cleaned_data):
    """Test recommendation engine edge cases."""
    # Single car in database
    single_car = pd.DataFrame({
        'year': [2018],
        'price': [2500000],
        'mileage': [45000],
        'engine_capacity': [1300],
        'transmission': ['Manual']
    })
    
    with pytest.raises(ValueError):
        get_similar_cars(single_car.iloc[0], single_car, 2)
    
    # Request more recommendations than available cars
    with pytest.raises(ValueError):
        get_similar_cars(
            sample_cleaned_data.iloc[0],
            sample_cleaned_data,
            len(sample_cleaned_data) + 1
        )
