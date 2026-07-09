#!/bin/bash
set -e

# Create necessary directories
mkdir -p data/raw data/cleaned logs models

# Initialize the database
python database/create_pakwheels_table.sql

# Train initial models if they don't exist
if [ ! -f "models/best_xgb_model_updated.joblib" ]; then
    echo "Training initial models..."
    python models/train_and_tune_models.py
fi

# Run data cleaning if needed
if [ ! -f "data/cleaned/pakwheels_listings_cleaned.csv" ]; then
    echo "Cleaning data..."
    python data_processing/clean_and_preprocess.py
fi

echo "Initialization complete!"
