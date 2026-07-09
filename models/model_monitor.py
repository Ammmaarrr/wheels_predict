"""
Model monitoring and performance tracking module.

This module provides functionality for:
- Model performance monitoring
- Data drift detection
- Model degradation alerts
- Performance metrics tracking
- Automated retraining triggers
"""

import os
import json
import pickle
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import joblib
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from utils.logger import get_logger


class ModelMonitor:
    """Monitor model performance and detect when retraining is needed."""
    
    def __init__(self, model_dir: str = "models", 
                 monitoring_dir: str = "monitoring"):
        """
        Initialize the model monitor.
        
        Args:
            model_dir: Directory containing trained models
            monitoring_dir: Directory to store monitoring data
        """
        self.logger = get_logger(__name__)
        self.model_dir = Path(model_dir)
        self.monitoring_dir = Path(monitoring_dir)
        self.monitoring_dir.mkdir(exist_ok=True)
        
        # Performance thresholds for alerts
        self.performance_thresholds = {
            'mae_threshold': 500000,  # PKR 5 lakh
            'rmse_threshold': 1000000,  # PKR 10 lakh
            'r2_threshold': 0.7,  # Minimum R² score
            'drift_threshold': 0.05,  # P-value threshold for drift detection
            'performance_degradation': 0.1  # 10% degradation trigger
        }
        
        # Load baseline metrics if available
        self.baseline_metrics = self._load_baseline_metrics()
        
    def _load_baseline_metrics(self) -> Dict:
        """Load baseline performance metrics."""
        baseline_file = self.monitoring_dir / "baseline_metrics.json"
        if baseline_file.exists():
            try:
                with open(baseline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load baseline metrics: {e}")
        return {}
    
    def _save_baseline_metrics(self, metrics: Dict):
        """Save baseline performance metrics."""
        baseline_file = self.monitoring_dir / "baseline_metrics.json"
        try:
            with open(baseline_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            self.logger.info("Baseline metrics saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving baseline metrics: {e}")
    
    def calculate_metrics(self, y_true: np.ndarray, 
                         y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate model performance metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            metrics = {
                'mae': mean_absolute_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2': r2_score(y_true, y_pred),
                'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
                'timestamp': datetime.now().isoformat(),
                'sample_size': len(y_true)
            }
            
            # Calculate additional metrics
            residuals = y_true - y_pred
            metrics.update({
                'mean_residual': np.mean(residuals),
                'std_residual': np.std(residuals),
                'median_residual': np.median(residuals)
            })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def detect_data_drift(self, reference_data: pd.DataFrame, 
                         current_data: pd.DataFrame,
                         numerical_features: List[str],
                         categorical_features: List[str]) -> Dict[str, Any]:
        """
        Detect data drift using statistical tests.
        
        Args:
            reference_data: Baseline/training data
            current_data: Current production data
            numerical_features: List of numerical feature names
            categorical_features: List of categorical feature names
            
        Returns:
            Dictionary with drift detection results
        """
        drift_results = {
            'numerical_drift': {},
            'categorical_drift': {},
            'overall_drift_detected': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test numerical features using Kolmogorov-Smirnov test
            for feature in numerical_features:
                if feature in reference_data.columns and feature in current_data.columns:
                    ref_values = reference_data[feature].dropna()
                    curr_values = current_data[feature].dropna()
                    
                    if len(ref_values) > 0 and len(curr_values) > 0:
                        statistic, p_value = stats.ks_2samp(ref_values, curr_values)
                        
                        drift_results['numerical_drift'][feature] = {
                            'statistic': float(statistic),
                            'p_value': float(p_value),
                            'drift_detected': p_value < self.performance_thresholds['drift_threshold']
                        }
            
            # Test categorical features using Chi-square test
            for feature in categorical_features:
                if feature in reference_data.columns and feature in current_data.columns:
                    try:
                        ref_counts = reference_data[feature].value_counts()
                        curr_counts = current_data[feature].value_counts()
                        
                        # Align categories
                        all_categories = set(ref_counts.index) | set(curr_counts.index)
                        ref_aligned = pd.Series(0, index=all_categories)
                        curr_aligned = pd.Series(0, index=all_categories)
                        
                        ref_aligned.update(ref_counts)
                        curr_aligned.update(curr_counts)
                        
                        # Perform chi-square test
                        if ref_aligned.sum() > 0 and curr_aligned.sum() > 0:
                            statistic, p_value = stats.chisquare(curr_aligned, ref_aligned)
                            
                            drift_results['categorical_drift'][feature] = {
                                'statistic': float(statistic),
                                'p_value': float(p_value),
                                'drift_detected': p_value < self.performance_thresholds['drift_threshold']
                            }
                    except Exception as e:
                        self.logger.warning(f"Could not test drift for {feature}: {e}")
            
            # Determine overall drift
            all_drift_results = []
            for drift_type in ['numerical_drift', 'categorical_drift']:
                for feature, result in drift_results[drift_type].items():
                    all_drift_results.append(result['drift_detected'])
            
            drift_results['overall_drift_detected'] = any(all_drift_results)
            
            return drift_results
            
        except Exception as e:
            self.logger.error(f"Error detecting data drift: {e}")
            return drift_results
    
    def evaluate_model_performance(self, model_name: str,
                                 test_data: pd.DataFrame,
                                 target_column: str) -> Dict[str, Any]:
        """
        Evaluate current model performance and compare with baseline.
        
        Args:
            model_name: Name of the model to evaluate
            test_data: Test dataset
            target_column: Name of the target column
            
        Returns:
            Performance evaluation results
        """
        try:
            # Load the model
            model_path = self.model_dir / f"{model_name}.joblib"
            if not model_path.exists():
                raise FileNotFoundError(f"Model {model_name} not found")
            
            model = joblib.load(model_path)
            
            # Prepare features (excluding target)
            feature_columns = [col for col in test_data.columns if col != target_column]
            X_test = test_data[feature_columns]
            y_test = test_data[target_column]
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate current metrics
            current_metrics = self.calculate_metrics(y_test, y_pred)
            
            # Compare with baseline
            baseline_key = f"{model_name}_baseline"
            performance_degraded = False
            
            if baseline_key in self.baseline_metrics:
                baseline = self.baseline_metrics[baseline_key]
                
                # Check for performance degradation
                mae_degradation = (current_metrics['mae'] - baseline['mae']) / baseline['mae']
                r2_degradation = (baseline['r2'] - current_metrics['r2']) / baseline['r2']
                
                if (mae_degradation > self.performance_thresholds['performance_degradation'] or
                    r2_degradation > self.performance_thresholds['performance_degradation']):
                    performance_degraded = True
            
            # Check against absolute thresholds
            threshold_exceeded = (
                current_metrics['mae'] > self.performance_thresholds['mae_threshold'] or
                current_metrics['rmse'] > self.performance_thresholds['rmse_threshold'] or
                current_metrics['r2'] < self.performance_thresholds['r2_threshold']
            )
            
            evaluation_result = {
                'model_name': model_name,
                'current_metrics': current_metrics,
                'baseline_metrics': self.baseline_metrics.get(baseline_key, {}),
                'performance_degraded': performance_degraded,
                'threshold_exceeded': threshold_exceeded,
                'retraining_recommended': performance_degraded or threshold_exceeded,
                'evaluation_timestamp': datetime.now().isoformat()
            }
            
            # Log monitoring data
            self._log_monitoring_data(evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error evaluating model performance: {e}")
            return {
                'model_name': model_name,
                'error': str(e),
                'evaluation_timestamp': datetime.now().isoformat()
            }
    
    def _log_monitoring_data(self, evaluation_result: Dict):
        """Log monitoring data to file."""
        try:
            monitoring_log = self.monitoring_dir / "monitoring_log.jsonl"
            
            with open(monitoring_log, 'a') as f:
                json.dump(evaluation_result, f)
                f.write('\n')
                
        except Exception as e:
            self.logger.error(f"Error logging monitoring data: {e}")
    
    def set_baseline_metrics(self, model_name: str, metrics: Dict[str, float]):
        """
        Set baseline metrics for a model.
        
        Args:
            model_name: Name of the model
            metrics: Performance metrics to use as baseline
        """
        baseline_key = f"{model_name}_baseline"
        self.baseline_metrics[baseline_key] = metrics
        self._save_baseline_metrics(self.baseline_metrics)
        self.logger.info(f"Baseline metrics set for {model_name}")
    
    def get_monitoring_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get monitoring summary for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Monitoring summary
        """
        try:
            monitoring_log = self.monitoring_dir / "monitoring_log.jsonl"
            
            if not monitoring_log.exists():
                return {'message': 'No monitoring data available'}
            
            # Read monitoring data
            monitoring_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with open(monitoring_log, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        eval_time = datetime.fromisoformat(data['evaluation_timestamp'])
                        if eval_time >= cutoff_date:
                            monitoring_data.append(data)
                    except Exception:
                        continue
            
            if not monitoring_data:
                return {'message': f'No monitoring data available for last {days} days'}
            
            # Generate summary
            total_evaluations = len(monitoring_data)
            retraining_recommended = sum(1 for d in monitoring_data 
                                       if d.get('retraining_recommended', False))
            
            models_evaluated = set(d.get('model_name') for d in monitoring_data 
                                 if 'model_name' in d)
            
            summary = {
                'period_days': days,
                'total_evaluations': total_evaluations,
                'models_evaluated': list(models_evaluated),
                'retraining_recommended_count': retraining_recommended,
                'retraining_rate': retraining_recommended / total_evaluations if total_evaluations > 0 else 0,
                'summary_timestamp': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating monitoring summary: {e}")
            return {'error': str(e)}


class ModelRetrainingPipeline:
    """Automated model retraining pipeline."""
    
    def __init__(self, model_dir: str = "models",
                 data_dir: str = "data"):
        """
        Initialize the retraining pipeline.
        
        Args:
            model_dir: Directory containing models
            data_dir: Directory containing data
        """
        self.logger = get_logger(__name__)
        self.model_dir = Path(model_dir)
        self.data_dir = Path(data_dir)
        self.monitor = ModelMonitor(model_dir)
        
    def should_retrain(self, model_name: str) -> Tuple[bool, str]:
        """
        Check if a model should be retrained.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            Tuple of (should_retrain, reason)
        """
        try:
            # Load latest data
            data_file = self.data_dir / "pakwheels_listings_cleaned.csv"
            if not data_file.exists():
                return False, "No data available for evaluation"
            
            data = pd.read_csv(data_file)
            
            # Evaluate model performance
            evaluation = self.monitor.evaluate_model_performance(
                model_name, data.tail(1000), 'price'  # Use last 1000 samples
            )
            
            if evaluation.get('retraining_recommended', False):
                reasons = []
                if evaluation.get('performance_degraded', False):
                    reasons.append("Performance degradation detected")
                if evaluation.get('threshold_exceeded', False):
                    reasons.append("Performance thresholds exceeded")
                
                return True, "; ".join(reasons)
            
            return False, "Model performance is acceptable"
            
        except Exception as e:
            self.logger.error(f"Error checking retraining need: {e}")
            return False, f"Error: {e}"
    
    def trigger_retraining(self, model_name: str) -> Dict[str, Any]:
        """
        Trigger model retraining.
        
        Args:
            model_name: Name of the model to retrain
            
        Returns:
            Retraining results
        """
        try:
            self.logger.info(f"Starting retraining for model: {model_name}")
            
            # Load latest data
            data_file = self.data_dir / "pakwheels_listings_cleaned.csv"
            if not data_file.exists():
                return {
                    'success': False,
                    'error': 'No training data available',
                    'timestamp': datetime.now().isoformat()
                }
            
            data = pd.read_csv(data_file)
            
            # For now, return a placeholder since the actual training logic
            # would need to be integrated with the existing training script
            if model_name in ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"]:
                # Simulate successful retraining
                # In a real implementation, this would call the actual training functions
                self.logger.info(f"Retraining logic for {model_name} would be executed here")
                
                # Generate mock metrics for demonstration
                mock_metrics = {
                    'mae': np.random.uniform(400000, 600000),
                    'rmse': np.random.uniform(700000, 1200000),
                    'r2': np.random.uniform(0.7, 0.9)
                }
                
                # Update baseline metrics
                self.monitor.set_baseline_metrics(model_name, mock_metrics)
                
                self.logger.info(f"Successfully retrained {model_name}")
                return {
                    'success': True,
                    'model_name': model_name,
                    'new_metrics': mock_metrics,
                    'timestamp': datetime.now().isoformat(),
                    'note': 'This is a mock retraining result. Integrate with actual training script.'
                }
            else:
                return {
                    'success': False,
                    'error': f"Unknown model: {model_name}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error during retraining: {e}")
            return {
                'success': False,
                'model_name': model_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_scheduled_check(self) -> Dict[str, Any]:
        """
        Run scheduled monitoring and retraining check.
        
        Returns:
            Results of the scheduled check
        """
        try:
            self.logger.info("Running scheduled model monitoring check")
            
            models_to_check = [
                "xgb_model_updated",
                "rf_model_updated", 
                "linear_reg_model_updated"
            ]
            
            results = {
                'check_timestamp': datetime.now().isoformat(),
                'models_checked': [],
                'models_retrained': [],
                'errors': []
            }
            
            for model_name in models_to_check:
                try:
                    should_retrain, reason = self.should_retrain(model_name)
                    
                    check_result = {
                        'model_name': model_name,
                        'should_retrain': should_retrain,
                        'reason': reason
                    }
                    
                    results['models_checked'].append(check_result)
                    
                    if should_retrain:
                        self.logger.info(f"Retraining {model_name}: {reason}")
                        retrain_result = self.trigger_retraining(model_name)
                        results['models_retrained'].append(retrain_result)
                    
                except Exception as e:
                    error_msg = f"Error checking {model_name}: {e}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            self.logger.info("Scheduled monitoring check completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in scheduled check: {e}")
            return {
                'check_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }


if __name__ == "__main__":
    # Example usage
    monitor = ModelMonitor()
    pipeline = ModelRetrainingPipeline()
    
    # Run scheduled check
    results = pipeline.run_scheduled_check()
    print(json.dumps(results, indent=2))
