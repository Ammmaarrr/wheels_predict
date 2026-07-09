#!/usr/bin/env python3
"""
Simple web interface for Wheels Predict - Production Ready
Now serving the beautiful MVP frontend!
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = Flask(__name__, 
           template_folder='frontend_mvp/templates',
           static_folder='frontend_mvp/static')

@app.route('/')
def index():
    """Main page - Beautiful MVP Frontend"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Car price prediction endpoint"""
    try:
        data = request.get_json()
        
        # Extract car features
        brand = data.get('brand', 'Toyota')
        model = data.get('model', 'Unknown')
        year = data.get('year', 2020)
        mileage = data.get('mileage', 50000)
        engine_capacity = data.get('engine_capacity', 1.5)
        
        # Simple prediction logic (you can replace this with your ML model)
        base_price = 1500000  # Base price in PKR
        
        # Adjust for brand
        brand_multipliers = {
            'Toyota': 1.8, 'Honda': 1.7, 'Suzuki': 1.2, 'Hyundai': 1.4,
            'BMW': 3.5, 'Mercedes': 4.0, 'Audi': 3.2, 'Nissan': 1.5,
            'Kia': 1.3, 'Volkswagen': 2.0, 'Mitsubishi': 1.2
        }
        brand_mult = brand_multipliers.get(brand, 1.0)
        
        # Adjust for year (newer = more expensive)
        year_factor = max(0.3, (year - 1990) / 35)
        
        # Adjust for mileage (lower = more expensive)
        mileage_factor = max(0.4, 1.0 - (mileage / 300000))
        
        # Adjust for engine capacity
        engine_factor = min(2.0, max(0.8, engine_capacity))
        
        # Calculate predicted price
        predicted_price = int(base_price * brand_mult * year_factor * mileage_factor * engine_factor)
        
        # Calculate confidence (simplified)
        confidence = 0.75 if brand in brand_multipliers else 0.50
        
        return jsonify({
            'predicted_price': predicted_price,
            'confidence': confidence,
            'message': 'Prediction successful'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Prediction failed'
        }), 400

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Wheels Predict MVP is running!",
        "frontend": "Beautiful MVP Frontend",
        "prediction": "Available"
    })

@app.route('/api/docs')
def api_docs():
    """API documentation"""
    return jsonify({
        "message": "API Documentation",
        "endpoints": [
            "/health - Health check",
            "/predict - Price prediction (POST)",
            "/api/docs - This documentation"
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Wheels Predict MVP System...")
    print("📡 Server running on http://localhost:5000")
    print("🎨 Beautiful MVP Frontend ready!")
    print("✅ All systems ready!")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
