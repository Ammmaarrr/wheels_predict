"""
Model monitoring dashboard and API endpoints.

This module provides web endpoints for:
- Model performance monitoring
- Data drift visualization
- Retraining triggers
- Monitoring dashboards
"""

import json
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template
import pandas as pd

try:
    import plotly.graph_objs as go
    import plotly.utils
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from models.model_monitor import ModelMonitor, ModelRetrainingPipeline
from utils.logger import get_logger

# Create blueprint for monitoring routes
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')
logger = get_logger(__name__)


@monitoring_bp.route('/dashboard')
def dashboard():
    """Render the monitoring dashboard."""
    try:
        return render_template('monitoring_dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/metrics/<model_name>')
def get_model_metrics(model_name):
    """Get current metrics for a specific model."""
    try:
        monitor = ModelMonitor()
        
        # Load test data
        data = pd.read_csv('data/pakwheels_listings_cleaned.csv')
        evaluation = monitor.evaluate_model_performance(
            model_name, data.tail(500), 'price'
        )
        
        return jsonify(evaluation)
        
    except Exception as e:
        logger.error(f"Error getting metrics for {model_name}: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/metrics/all')
def get_all_metrics():
    """Get metrics for all models."""
    try:
        monitor = ModelMonitor()
        models = ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"]
        
        # Load test data
        data = pd.read_csv('data/pakwheels_listings_cleaned.csv')
        test_data = data.tail(500)
        
        all_metrics = {}
        for model_name in models:
            try:
                evaluation = monitor.evaluate_model_performance(
                    model_name, test_data, 'price'
                )
                all_metrics[model_name] = evaluation
            except Exception as e:
                all_metrics[model_name] = {'error': str(e)}
        
        return jsonify(all_metrics)
        
    except Exception as e:
        logger.error(f"Error getting all metrics: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/drift/<model_name>')
def check_data_drift(model_name):
    """Check for data drift in model features."""
    try:
        monitor = ModelMonitor()
        
        # Load reference and current data
        data = pd.read_csv('data/pakwheels_listings_cleaned.csv')
        
        # Use first 80% as reference, last 20% as current
        split_point = int(len(data) * 0.8)
        reference_data = data.iloc[:split_point]
        current_data = data.iloc[split_point:]
        
        # Define feature lists (adjust based on your actual features)
        numerical_features = ['mileage', 'engine_capacity', 'registration_year']
        categorical_features = ['make', 'model', 'fuel_type', 'transmission']
        
        # Filter features that actually exist
        numerical_features = [f for f in numerical_features if f in data.columns]
        categorical_features = [f for f in categorical_features if f in data.columns]
        
        drift_results = monitor.detect_data_drift(
            reference_data, current_data, 
            numerical_features, categorical_features
        )
        
        return jsonify(drift_results)
        
    except Exception as e:
        logger.error(f"Error checking drift for {model_name}: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/summary')
def get_monitoring_summary():
    """Get monitoring summary for the dashboard."""
    try:
        monitor = ModelMonitor()
        days = request.args.get('days', 30, type=int)
        
        summary = monitor.get_monitoring_summary(days)
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting monitoring summary: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/retrain/<model_name>', methods=['POST'])
def trigger_retraining(model_name):
    """Manually trigger model retraining."""
    try:
        pipeline = ModelRetrainingPipeline()
        
        # Check if retraining is needed
        should_retrain, reason = pipeline.should_retrain(model_name)
        
        force_retrain = request.json.get('force', False) if request.json else False
        
        if should_retrain or force_retrain:
            result = pipeline.trigger_retraining(model_name)
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'message': f'Retraining not needed: {reason}',
                'model_name': model_name
            })
        
    except Exception as e:
        logger.error(f"Error triggering retraining for {model_name}: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/retrain/check')
def check_retraining_needed():
    """Check which models need retraining."""
    try:
        pipeline = ModelRetrainingPipeline()
        models = ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"]
        
        results = {}
        for model_name in models:
            should_retrain, reason = pipeline.should_retrain(model_name)
            results[model_name] = {
                'should_retrain': should_retrain,
                'reason': reason
            }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error checking retraining needs: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/retrain/scheduled', methods=['POST'])
def run_scheduled_check():
    """Run the scheduled monitoring and retraining check."""
    try:
        pipeline = ModelRetrainingPipeline()
        results = pipeline.run_scheduled_check()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error running scheduled check: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/performance/history/<model_name>')
def get_performance_history(model_name):
    """Get performance history for a model."""
    try:
        monitor = ModelMonitor()
        
        # Read monitoring log
        monitoring_log = monitor.monitoring_dir / "monitoring_log.jsonl"
        if not monitoring_log.exists():
            return jsonify({'message': 'No monitoring history available'})
        
        history = []
        with open(monitoring_log, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('model_name') == model_name:
                        history.append(data)
                except Exception:
                    continue
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('evaluation_timestamp', ''))
        
        return jsonify({
            'model_name': model_name,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting performance history for {model_name}: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/alerts')
def get_alerts():
    """Get current alerts and warnings."""
    try:
        monitor = ModelMonitor()
        models = ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"]
        
        alerts = []
        
        # Load test data
        data = pd.read_csv('data/pakwheels_listings_cleaned.csv')
        test_data = data.tail(500)
        
        for model_name in models:
            try:
                evaluation = monitor.evaluate_model_performance(
                    model_name, test_data, 'price'
                )
                
                if evaluation.get('retraining_recommended', False):
                    alert = {
                        'type': 'warning',
                        'model': model_name,
                        'message': 'Model retraining recommended',
                        'timestamp': evaluation.get('evaluation_timestamp'),
                        'details': {
                            'performance_degraded': evaluation.get('performance_degraded', False),
                            'threshold_exceeded': evaluation.get('threshold_exceeded', False)
                        }
                    }
                    alerts.append(alert)
                    
            except Exception as e:
                alerts.append({
                    'type': 'error',
                    'model': model_name,
                    'message': f'Error evaluating model: {e}',
                    'timestamp': datetime.now().isoformat()
                })
        
        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/charts/performance/<model_name>')
def get_performance_chart(model_name):
    """Generate performance chart data for a model."""
    try:
        if not HAS_PLOTLY:
            return jsonify({
                'error': 'Plotly not available. Install with: pip install plotly',
                'message': 'Charts require plotly library'
            }), 501
        
        monitor = ModelMonitor()
        
        # Get performance history
        monitoring_log = monitor.monitoring_dir / "monitoring_log.jsonl"
        if not monitoring_log.exists():
            return jsonify({'message': 'No data available for chart'})
        
        history = []
        with open(monitoring_log, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('model_name') == model_name:
                        history.append(data)
                except Exception:
                    continue
        
        if not history:
            return jsonify({'message': 'No history available for this model'})
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('evaluation_timestamp', ''))
        
        # Extract data for charts
        timestamps = []
        mae_values = []
        r2_values = []
        
        for entry in history:
            if 'current_metrics' in entry:
                timestamps.append(entry['evaluation_timestamp'])
                mae_values.append(entry['current_metrics'].get('mae', 0))
                r2_values.append(entry['current_metrics'].get('r2', 0))
        
        # Create Plotly charts
        fig_mae = go.Figure()
        fig_mae.add_trace(go.Scatter(
            x=timestamps,
            y=mae_values,
            mode='lines+markers',
            name='MAE',
            line=dict(color='red')
        ))
        fig_mae.update_layout(
            title=f'MAE Trend - {model_name}',
            xaxis_title='Time',
            yaxis_title='Mean Absolute Error'
        )
        
        fig_r2 = go.Figure()
        fig_r2.add_trace(go.Scatter(
            x=timestamps,
            y=r2_values,
            mode='lines+markers',
            name='R²',
            line=dict(color='blue')
        ))
        fig_r2.update_layout(
            title=f'R² Trend - {model_name}',
            xaxis_title='Time',
            yaxis_title='R² Score'
        )
        
        return jsonify({
            'mae_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig_mae)),
            'r2_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig_r2)),
            'data_points': len(timestamps)
        })
        
    except Exception as e:
        logger.error(f"Error generating charts for {model_name}: {e}")
        return jsonify({'error': str(e)}), 500
