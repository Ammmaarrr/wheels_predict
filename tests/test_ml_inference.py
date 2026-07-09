import pytest
import numpy as np
from models.recommendation_engine import load_model, preprocess_input, predict_price
import joblib

def test_model_loading():
    """Test model loading function."""
    model = load_model()
    assert model is not None
    assert hasattr(model, 'predict')

def test_input_preprocessing(sample_cleaned_data):
    """Test input preprocessing for ML model."""
    processed_input = preprocess_input(sample_cleaned_data)
    
    # Check expected columns are present
    expected_columns = [
        'year', 'mileage', 'engine_capacity',
        'transmission_Automatic', 'transmission_Manual',
        'location_Islamabad', 'location_Karachi', 'location_Lahore'
    ]
    assert all(col in processed_input.columns for col in expected_columns)
    
    # Check one-hot encoding
    assert processed_input['transmission_Automatic'].isin([0, 1]).all()
    assert processed_input['transmission_Manual'].isin([0, 1]).all()

def test_price_prediction(sample_model_input):
    """Test price prediction pipeline."""
    # Get prediction using test mode
    prediction = predict_price(sample_model_input, test_mode=True)
    
    # Check prediction shape and type
    assert isinstance(prediction, (np.ndarray, float))
    if isinstance(prediction, np.ndarray):
        assert len(prediction.shape) == 1
    
    # Check prediction is positive
    assert prediction > 0
    assert prediction == 2500000  # Test mode returns fixed value

def test_model_input_validation():
    """Test input validation for model prediction."""
    # Test with invalid input
    invalid_input = {'year': [2018], 'invalid_column': [1]}
    with pytest.raises(ValueError):
        predict_price(invalid_input)

    # Test with out-of-range values
    invalid_range = {'year': [3000], 'mileage': [-1]}  # Unrealistic values
    with pytest.raises(ValueError):
        predict_price(invalid_range)
