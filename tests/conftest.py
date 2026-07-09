import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_raw_data():
    """Fixture providing sample raw car listing data for testing."""
    return pd.DataFrame({
        'price': ['PKR 2,500,000', 'PKR 3,400,000', 'PKR 1,800,000'],
        'year': [2018, 2020, 2015],
        'mileage': ['45,000 km', '12,000 km', '80,000 km'],
        'location': ['Lahore', 'Karachi', 'Islamabad'],
        'engine_capacity': ['1300 cc', '1800 cc', '1000 cc'],
        'transmission': ['Manual', 'Automatic', 'Manual']
    })

@pytest.fixture
def sample_cleaned_data():
    """Fixture providing sample cleaned car listing data for testing."""
    return pd.DataFrame({
        'price': [2500000, 3400000, 1800000],
        'year': [2018, 2020, 2015],
        'mileage': [45000, 12000, 80000],
        'location': ['Lahore', 'Karachi', 'Islamabad'],
        'engine_capacity': [1300, 1800, 1000],
        'transmission': ['Manual', 'Automatic', 'Manual']
    })

@pytest.fixture
def sample_model_input():
    """Fixture providing sample formatted input for ML models."""
    return pd.DataFrame({
        'year': [2018],
        'mileage': [45000],
        'engine_capacity': [1300],
        'transmission_Automatic': [0],
        'transmission_Manual': [1],
        'location_Islamabad': [0],
        'location_Karachi': [0],
        'location_Lahore': [1]
    })
