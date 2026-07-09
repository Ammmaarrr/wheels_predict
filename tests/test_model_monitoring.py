"""
Tests for model monitoring and retraining functionality.
"""

import pytest
import pandas as pd
import numpy as np
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import modules to test
from models.model_monitor import ModelMonitor, ModelRetrainingPipeline


class TestModelMonitor:
    """Test cases for ModelMonitor class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_model_dir = tempfile.mkdtemp()
        temp_monitoring_dir = tempfile.mkdtemp()
        
        yield temp_model_dir, temp_monitoring_dir
        
        # Cleanup
        shutil.rmtree(temp_model_dir, ignore_errors=True)
        shutil.rmtree(temp_monitoring_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        data = pd.DataFrame({
            'price': np.random.normal(1000000, 300000, 1000),
            'mileage': np.random.normal(50000, 20000, 1000),
            'engine_capacity': np.random.choice([1000, 1300, 1600, 2000], 1000),
            'registration_year': np.random.choice(range(2010, 2024), 1000),
            'make': np.random.choice(['Toyota', 'Honda', 'Suzuki'], 1000),
            'model': np.random.choice(['Corolla', 'Civic', 'Alto'], 1000),
            'fuel_type': np.random.choice(['Petrol', 'Diesel'], 1000),
            'transmission': np.random.choice(['Manual', 'Automatic'], 1000)
        })
        return data
    
    def test_monitor_initialization(self, temp_dirs):
        """Test ModelMonitor initialization."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        assert monitor.model_dir == Path(model_dir)
        assert monitor.monitoring_dir == Path(monitoring_dir)
        assert Path(monitoring_dir).exists()
        assert isinstance(monitor.performance_thresholds, dict)
    
    def test_calculate_metrics(self, temp_dirs):
        """Test metrics calculation."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Create sample true and predicted values
        y_true = np.array([1000000, 1200000, 800000, 1500000])
        y_pred = np.array([950000, 1150000, 850000, 1450000])
        
        metrics = monitor.calculate_metrics(y_true, y_pred)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert 'mape' in metrics
        assert 'timestamp' in metrics
        assert 'sample_size' in metrics
        
        assert metrics['sample_size'] == 4
        assert metrics['mae'] > 0
        assert metrics['rmse'] > 0
        assert 0 <= metrics['r2'] <= 1
    
    def test_detect_data_drift_numerical(self, temp_dirs, sample_data):
        """Test numerical data drift detection."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Create reference and current data (same distribution)
        reference_data = sample_data.iloc[:500]
        current_data = sample_data.iloc[500:]
        
        numerical_features = ['mileage', 'engine_capacity', 'registration_year']
        categorical_features = ['make', 'model', 'fuel_type', 'transmission']
        
        drift_results = monitor.detect_data_drift(
            reference_data, current_data,
            numerical_features, categorical_features
        )
        
        assert 'numerical_drift' in drift_results
        assert 'categorical_drift' in drift_results
        assert 'overall_drift_detected' in drift_results
        assert 'timestamp' in drift_results
        
        # Check that all features were tested
        for feature in numerical_features:
            assert feature in drift_results['numerical_drift']
            assert 'p_value' in drift_results['numerical_drift'][feature]
            assert 'drift_detected' in drift_results['numerical_drift'][feature]
    
    def test_detect_data_drift_with_drift(self, temp_dirs):
        """Test data drift detection with actual drift."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Create reference data
        np.random.seed(42)
        reference_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 500),
            'category1': np.random.choice(['A', 'B', 'C'], 500, p=[0.5, 0.3, 0.2])
        })
        
        # Create drifted current data
        current_data = pd.DataFrame({
            'feature1': np.random.normal(2, 1, 500),  # Shifted mean
            'category1': np.random.choice(['A', 'B', 'C'], 500, p=[0.2, 0.3, 0.5])  # Different distribution
        })
        
        drift_results = monitor.detect_data_drift(
            reference_data, current_data,
            ['feature1'], ['category1']
        )
        
        # Should detect drift in both features
        assert drift_results['numerical_drift']['feature1']['drift_detected']
        assert drift_results['categorical_drift']['category1']['drift_detected']
        assert drift_results['overall_drift_detected']
    
    def test_baseline_metrics_management(self, temp_dirs):
        """Test baseline metrics saving and loading."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Set baseline metrics
        test_metrics = {
            'mae': 100000,
            'rmse': 150000,
            'r2': 0.85
        }
        monitor.set_baseline_metrics('test_model', test_metrics)
        
        # Check if metrics were saved
        baseline_file = Path(monitoring_dir) / "baseline_metrics.json"
        assert baseline_file.exists()
        
        # Load and verify
        with open(baseline_file, 'r') as f:
            saved_metrics = json.load(f)
        
        assert 'test_model_baseline' in saved_metrics
        assert saved_metrics['test_model_baseline'] == test_metrics
    
    @patch('models.model_monitor.joblib.load')
    def test_evaluate_model_performance(self, mock_joblib_load, temp_dirs, sample_data):
        """Test model performance evaluation."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Create a mock model
        mock_model = Mock()
        mock_model.predict.return_value = np.random.normal(1000000, 100000, len(sample_data))
        mock_joblib_load.return_value = mock_model
        
        # Create a fake model file
        model_file = Path(model_dir) / "test_model.joblib"
        model_file.touch()
        
        evaluation = monitor.evaluate_model_performance(
            'test_model', sample_data, 'price'
        )
        
        assert 'model_name' in evaluation
        assert 'current_metrics' in evaluation
        assert 'retraining_recommended' in evaluation
        assert 'evaluation_timestamp' in evaluation
        
        assert evaluation['model_name'] == 'test_model'
        assert isinstance(evaluation['retraining_recommended'], bool)
    
    def test_monitoring_summary(self, temp_dirs):
        """Test monitoring summary generation."""
        model_dir, monitoring_dir = temp_dirs
        monitor = ModelMonitor(model_dir, monitoring_dir)
        
        # Create some fake monitoring data
        monitoring_log = Path(monitoring_dir) / "monitoring_log.jsonl"
        
        test_data = [
            {
                'model_name': 'test_model1',
                'retraining_recommended': False,
                'evaluation_timestamp': datetime.now().isoformat()
            },
            {
                'model_name': 'test_model2',
                'retraining_recommended': True,
                'evaluation_timestamp': datetime.now().isoformat()
            }
        ]
        
        with open(monitoring_log, 'w') as f:
            for data in test_data:
                json.dump(data, f)
                f.write('\n')
        
        summary = monitor.get_monitoring_summary(days=30)
        
        assert 'total_evaluations' in summary
        assert 'retraining_recommended_count' in summary
        assert 'models_evaluated' in summary
        assert summary['total_evaluations'] == 2
        assert summary['retraining_recommended_count'] == 1


class TestModelRetrainingPipeline:
    """Test cases for ModelRetrainingPipeline class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_model_dir = tempfile.mkdtemp()
        temp_data_dir = tempfile.mkdtemp()
        
        yield temp_model_dir, temp_data_dir
        
        # Cleanup
        shutil.rmtree(temp_model_dir, ignore_errors=True)
        shutil.rmtree(temp_data_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_data_file(self, temp_dirs):
        """Create sample data file for testing."""
        model_dir, data_dir = temp_dirs
        
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame({
            'price': np.random.normal(1000000, 300000, 1000),
            'mileage': np.random.normal(50000, 20000, 1000),
            'engine_capacity': np.random.choice([1000, 1300, 1600, 2000], 1000),
            'make': np.random.choice(['Toyota', 'Honda', 'Suzuki'], 1000)
        })
        
        data_file = Path(data_dir) / "wheels_predict_listings_cleaned.csv"
        data.to_csv(data_file, index=False)
        
        return data_file
    
    def test_pipeline_initialization(self, temp_dirs):
        """Test ModelRetrainingPipeline initialization."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        assert pipeline.model_dir == Path(model_dir)
        assert pipeline.data_dir == Path(data_dir)
        assert isinstance(pipeline.monitor, ModelMonitor)
    
    @patch('models.model_monitor.ModelMonitor.evaluate_model_performance')
    def test_should_retrain(self, mock_evaluate, temp_dirs, sample_data_file):
        """Test should_retrain decision logic."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        # Mock evaluation that recommends retraining
        mock_evaluate.return_value = {
            'retraining_recommended': True,
            'performance_degraded': True,
            'threshold_exceeded': False
        }
        
        should_retrain, reason = pipeline.should_retrain('test_model')
        
        assert should_retrain == True
        assert 'Performance degradation detected' in reason
    
    @patch('models.model_monitor.ModelMonitor.evaluate_model_performance')
    def test_should_not_retrain(self, mock_evaluate, temp_dirs, sample_data_file):
        """Test should_retrain when retraining is not needed."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        # Mock evaluation that doesn't recommend retraining
        mock_evaluate.return_value = {
            'retraining_recommended': False,
            'performance_degraded': False,
            'threshold_exceeded': False
        }
        
        should_retrain, reason = pipeline.should_retrain('test_model')
        
        assert should_retrain == False
        assert reason == "Model performance is acceptable"
    
    def test_trigger_retraining_success(self, temp_dirs, sample_data_file):
        """Test successful model retraining."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        result = pipeline.trigger_retraining('xgb_model_updated')
        
        assert result['success'] == True
        assert 'new_metrics' in result
        assert 'timestamp' in result
        assert 'note' in result  # Mock implementation note
    
    def test_trigger_retraining_failure(self, temp_dirs, sample_data_file):
        """Test failed model retraining."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        # Remove the data file to cause failure
        sample_data_file.unlink()
        
        result = pipeline.trigger_retraining('xgb_model_updated')
        
        assert result['success'] == False
        assert 'error' in result
        assert 'No training data available' in result['error']
    
    def test_trigger_retraining_unknown_model(self, temp_dirs, sample_data_file):
        """Test retraining with unknown model name."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        result = pipeline.trigger_retraining('unknown_model')
        
        assert result['success'] == False
        assert 'Unknown model' in result['error']
    
    @patch('models.model_monitor.ModelRetrainingPipeline.should_retrain')
    @patch('models.model_monitor.ModelRetrainingPipeline.trigger_retraining')
    def test_run_scheduled_check(self, mock_trigger, mock_should_retrain, temp_dirs, sample_data_file):
        """Test scheduled monitoring check."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        # Mock responses
        mock_should_retrain.side_effect = [
            (True, "Performance degraded"),   # First model needs retraining
            (False, "Good performance"),      # Second model is fine
            (True, "Threshold exceeded")      # Third model needs retraining
        ]
        
        mock_trigger.side_effect = [
            {'success': True, 'model_name': 'model1'},
            {'success': False, 'model_name': 'model3', 'error': 'Training failed'}
        ]
        
        results = pipeline.run_scheduled_check()
        
        assert 'check_timestamp' in results
        assert 'models_checked' in results
        assert 'models_retrained' in results
        assert len(results['models_checked']) == 3
        assert len(results['models_retrained']) == 2
    
    def test_data_file_missing(self, temp_dirs):
        """Test behavior when data file is missing."""
        model_dir, data_dir = temp_dirs
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        should_retrain, reason = pipeline.should_retrain('test_model')
        
        assert should_retrain == False
        assert "No data available" in reason


class TestMonitoringIntegration:
    """Integration tests for monitoring components."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_model_dir = tempfile.mkdtemp()
        temp_monitoring_dir = tempfile.mkdtemp()
        temp_data_dir = tempfile.mkdtemp()
        
        yield temp_model_dir, temp_monitoring_dir, temp_data_dir
        
        # Cleanup
        shutil.rmtree(temp_model_dir, ignore_errors=True)
        shutil.rmtree(temp_monitoring_dir, ignore_errors=True)
        shutil.rmtree(temp_data_dir, ignore_errors=True)
    
    def test_end_to_end_monitoring_workflow(self, temp_dirs):
        """Test complete monitoring workflow."""
        model_dir, monitoring_dir, data_dir = temp_dirs
        
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame({
            'price': np.random.normal(1000000, 300000, 1000),
            'mileage': np.random.normal(50000, 20000, 1000),
            'engine_capacity': np.random.choice([1000, 1300, 1600, 2000], 1000),
        })
        data_file = Path(data_dir) / "wheels_predict_listings_cleaned.csv"
        data.to_csv(data_file, index=False)
        
        # Initialize monitoring components
        monitor = ModelMonitor(model_dir, monitoring_dir)
        pipeline = ModelRetrainingPipeline(model_dir, data_dir)
        
        # Test metrics calculation
        y_true = data['price'].values[:100]
        y_pred = y_true + np.random.normal(0, 50000, 100)  # Add some noise
        
        metrics = monitor.calculate_metrics(y_true, y_pred)
        
        assert metrics['mae'] > 0
        assert 0 <= metrics['r2'] <= 1
        
        # Test baseline setting and retrieval
        monitor.set_baseline_metrics('test_model', metrics)
        
        baseline_file = Path(monitoring_dir) / "baseline_metrics.json"
        assert baseline_file.exists()
        
        # Test monitoring log
        evaluation_result = {
            'model_name': 'test_model',
            'current_metrics': metrics,
            'retraining_recommended': False,
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
        monitor._log_monitoring_data(evaluation_result)
        
        monitoring_log = Path(monitoring_dir) / "monitoring_log.jsonl"
        assert monitoring_log.exists()
        
        # Test summary generation
        summary = monitor.get_monitoring_summary(days=1)
        assert summary['total_evaluations'] >= 1
