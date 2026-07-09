import pytest
import pandas as pd
import numpy as np
from data_processing.clean_and_preprocess import clean_data, process_price, process_mileage, process_engine_capacity

def test_process_price():
    """Test price processing function."""
    # Test normal cases
    assert process_price('PKR 2,500,000') == 2500000
    assert process_price('PKR 1,234,567') == 1234567
    
    # Test edge cases
    assert process_price('PKR 0') == 0
    with pytest.raises(ValueError):
        process_price('Invalid Price')

def test_process_mileage():
    """Test mileage processing function."""
    # Test normal cases
    assert process_mileage('45,000 km') == 45000
    assert process_mileage('12,000 km') == 12000
    
    # Test edge cases
    assert process_mileage('0 km') == 0
    with pytest.raises(ValueError):
        process_mileage('Invalid Mileage')

def test_process_engine_capacity():
    """Test engine capacity processing function."""
    # Test normal cases
    assert process_engine_capacity('1300 cc') == 1300
    assert process_engine_capacity('1800 cc') == 1800
    
    # Test edge cases
    with pytest.raises(ValueError):
        process_engine_capacity('Invalid CC')

def test_clean_data(sample_raw_data, sample_cleaned_data):
    """Test the complete data cleaning pipeline."""
    # Process the sample raw data
    cleaned_df = clean_data(sample_raw_data)
    
    # Check if the output matches expected cleaned data
    pd.testing.assert_frame_equal(cleaned_df, sample_cleaned_data)
    
    # Check for no null values
    assert not cleaned_df.isnull().any().any()
    
    # Check data types
    assert cleaned_df['price'].dtype == np.int64
    assert cleaned_df['mileage'].dtype == np.int64
    assert cleaned_df['engine_capacity'].dtype == np.int64
