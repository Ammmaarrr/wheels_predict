"""
Script to generate sample monitoring data for testing the dashboard.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.model_monitor import ModelMonitor


def generate_sample_monitoring_data():
    """Generate sample monitoring data for dashboard testing."""
    
    monitor = ModelMonitor()
    
    # Generate sample data for the last 30 days
    models = ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"]
    
    print("Generating sample monitoring data...")
    
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        
        for model_name in models:
            # Generate realistic performance metrics with some variation
            base_mae = {
                "xgb_model_updated": 450000,
                "rf_model_updated": 520000,
                "linear_reg_model_updated": 680000
            }
            
            base_r2 = {
                "xgb_model_updated": 0.88,
                "rf_model_updated": 0.83,
                "linear_reg_model_updated": 0.75
            }
            
            # Add some degradation over time and random variation
            degradation_factor = 1 + (30 - i) * 0.001  # Slight degradation over time
            random_factor = np.random.uniform(0.95, 1.05)  # ±5% random variation
            
            mae = base_mae[model_name] * degradation_factor * random_factor
            r2 = base_r2[model_name] / (degradation_factor * random_factor)
            rmse = mae * 1.8  # Rough relationship
            
            # Create evaluation result
            evaluation_result = {
                'model_name': model_name,
                'current_metrics': {
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'mape': mae / 10000,  # Rough conversion
                    'timestamp': date.isoformat(),
                    'sample_size': 1000
                },
                'baseline_metrics': {
                    'mae': base_mae[model_name],
                    'rmse': base_mae[model_name] * 1.8,
                    'r2': base_r2[model_name]
                },
                'performance_degraded': mae > base_mae[model_name] * 1.1,
                'threshold_exceeded': mae > 500000 or r2 < 0.7,
                'retraining_recommended': mae > base_mae[model_name] * 1.15 or r2 < base_r2[model_name] * 0.9,
                'evaluation_timestamp': date.isoformat()
            }
            
            # Log the data
            monitor._log_monitoring_data(evaluation_result)
    
    print(f"Generated monitoring data for {len(models)} models over 30 days")
    print(f"Data saved to: {monitor.monitoring_dir / 'monitoring_log.jsonl'}")


def set_baseline_metrics():
    """Set baseline metrics for all models."""
    
    monitor = ModelMonitor()
    
    baselines = {
        "xgb_model_updated": {
            'mae': 450000,
            'rmse': 810000,
            'r2': 0.88
        },
        "rf_model_updated": {
            'mae': 520000,
            'rmse': 936000,
            'r2': 0.83
        },
        "linear_reg_model_updated": {
            'mae': 680000,
            'rmse': 1224000,
            'r2': 0.75
        }
    }
    
    for model_name, metrics in baselines.items():
        monitor.set_baseline_metrics(model_name, metrics)
        print(f"Set baseline metrics for {model_name}")


if __name__ == "__main__":
    # Create monitoring directory if it doesn't exist
    Path("monitoring").mkdir(exist_ok=True)
    
    # Generate sample data
    generate_sample_monitoring_data()
    set_baseline_metrics()
    
    print("\nSample data generation completed!")
    print("You can now refresh the monitoring dashboard to see the data.")
