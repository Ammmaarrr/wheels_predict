# Model Monitoring and Retraining System

This directory contains the model monitoring and retraining infrastructure for the PakWheels ML system.

## Components

### 1. Model Monitor (`models/model_monitor.py`)
- **Performance Tracking**: Monitors model performance metrics (MAE, RMSE, R²)
- **Data Drift Detection**: Detects changes in data distribution using statistical tests
- **Baseline Management**: Maintains and updates baseline performance metrics
- **Alert System**: Generates alerts when performance degrades or drift is detected

### 2. Monitoring API (`models/monitoring_api.py`)
- **REST Endpoints**: Provides API endpoints for monitoring dashboard
- **Performance Metrics**: Real-time access to model performance data
- **Drift Analysis**: API for data drift detection and visualization
- **Retraining Triggers**: Manual and automated retraining triggers

### 3. Monitoring Dashboard (`web/templates/monitoring_dashboard.html`)
- **Visual Dashboard**: Real-time monitoring dashboard with charts and metrics
- **Performance Overview**: Summary of all model performances
- **Alert Management**: Display and management of active alerts
- **Retraining Interface**: UI for triggering and monitoring retraining

### 4. Automated Retraining (`scripts/retrain_models.py`)
- **Scheduled Checks**: Automated performance evaluation and retraining
- **Configuration-Driven**: Configurable thresholds and parameters
- **Notification System**: Alerts and notifications for retraining events
- **Dry Run Mode**: Test retraining logic without actual execution

## Key Features

### Performance Monitoring
- **Real-time Metrics**: Continuous monitoring of model performance
- **Threshold Alerts**: Configurable thresholds for performance degradation
- **Historical Tracking**: Long-term performance trend analysis
- **Comparative Analysis**: Compare current performance with baselines

### Data Drift Detection
- **Statistical Tests**: Kolmogorov-Smirnov test for numerical features
- **Chi-square Test**: For categorical feature drift detection
- **Configurable Sensitivity**: Adjustable drift detection thresholds
- **Feature-level Analysis**: Individual feature drift analysis

### Automated Retraining
- **Performance-Based**: Triggers retraining when performance degrades
- **Drift-Based**: Retrains when significant data drift is detected
- **Scheduled Execution**: Regular automated checks and retraining
- **Rollback Capability**: Ability to rollback to previous models

### Notification System
- **Multi-channel Alerts**: Email, Slack, Teams notifications
- **Configurable Triggers**: Customizable alert conditions
- **Detailed Reports**: Comprehensive monitoring and retraining reports
- **GitHub Integration**: Automatic issue creation for failures

## Configuration

### Model Configuration (`config/model_config.json`)
```json
{
  "models": ["xgb_model_updated", "rf_model_updated", "linear_reg_model_updated"],
  "thresholds": {
    "mae_threshold": 500000,
    "rmse_threshold": 1000000,
    "r2_threshold": 0.7,
    "drift_threshold": 0.05,
    "performance_degradation": 0.1
  },
  "monitoring": {
    "check_interval_hours": 24,
    "baseline_update_threshold": 0.05
  },
  "retraining": {
    "auto_retrain": true,
    "backup_old_models": true,
    "validation_split": 0.2
  }
}
```

### Environment Variables
```bash
# Model monitoring
MODEL_DIR=models
DATA_DIR=data
MONITORING_DIR=monitoring
LOG_LEVEL=INFO

# Notification settings
SLACK_WEBHOOK_URL=your_slack_webhook
TEAMS_WEBHOOK_URL=your_teams_webhook
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

## Usage

### 1. Start Monitoring Dashboard
```bash
# Start the web interface with monitoring dashboard
python web/web_interface.py

# Access dashboard at http://localhost:5000/monitoring/dashboard
```

### 2. Manual Model Evaluation
```python
from models.model_monitor import ModelMonitor
import pandas as pd

# Initialize monitor
monitor = ModelMonitor()

# Load test data
data = pd.read_csv('data/pakwheels_listings_cleaned.csv')

# Evaluate model performance
evaluation = monitor.evaluate_model_performance(
    'xgb_model_updated', 
    data.tail(1000), 
    'price'
)

print(evaluation)
```

### 3. Check Data Drift
```python
from models.model_monitor import ModelMonitor
import pandas as pd

monitor = ModelMonitor()
data = pd.read_csv('data/pakwheels_listings_cleaned.csv')

# Split data for drift detection
split_point = int(len(data) * 0.8)
reference_data = data.iloc[:split_point]
current_data = data.iloc[split_point:]

# Check for drift
drift_results = monitor.detect_data_drift(
    reference_data, 
    current_data,
    ['mileage', 'engine_capacity', 'registration_year'],
    ['make', 'model', 'fuel_type', 'transmission']
)

print(drift_results)
```

### 4. Automated Retraining
```bash
# Check what models need retraining
python scripts/retrain_models.py --dry-run

# Retrain specific model
python scripts/retrain_models.py --model xgb_model_updated

# Force retrain all models
python scripts/retrain_models.py --force --notify

# Run scheduled check (used in CI/CD)
python scripts/retrain_models.py --notify
```

### 5. API Endpoints
- `GET /monitoring/api/metrics/all` - Get all model metrics
- `GET /monitoring/api/metrics/{model_name}` - Get specific model metrics
- `GET /monitoring/api/drift/{model_name}` - Check data drift
- `POST /monitoring/api/retrain/{model_name}` - Trigger retraining
- `GET /monitoring/api/alerts` - Get current alerts
- `GET /monitoring/api/summary` - Get monitoring summary

## GitHub Actions Integration

The monitoring system integrates with GitHub Actions for automated CI/CD:

### 1. Scheduled Monitoring (`.github/workflows/model-monitoring.yml`)
- Runs daily at 3 AM UTC
- Checks all models for performance degradation
- Automatically retrains models when needed
- Creates GitHub issues for failures
- Sends notifications to configured channels

### 2. Manual Triggers
```bash
# Manually trigger monitoring workflow
gh workflow run model-monitoring.yml

# Force retrain all models
gh workflow run model-monitoring.yml -f force_retrain=true
```

## Monitoring Data Structure

### Performance Metrics
```json
{
  "model_name": "xgb_model_updated",
  "current_metrics": {
    "mae": 450000,
    "rmse": 800000,
    "r2": 0.85,
    "mape": 12.5,
    "timestamp": "2025-01-15T10:30:00"
  },
  "baseline_metrics": {
    "mae": 400000,
    "rmse": 750000,
    "r2": 0.87
  },
  "performance_degraded": false,
  "retraining_recommended": false
}
```

### Drift Detection Results
```json
{
  "numerical_drift": {
    "mileage": {
      "statistic": 0.045,
      "p_value": 0.12,
      "drift_detected": false
    }
  },
  "categorical_drift": {
    "make": {
      "statistic": 15.3,
      "p_value": 0.02,
      "drift_detected": true
    }
  },
  "overall_drift_detected": true,
  "timestamp": "2025-01-15T10:30:00"
}
```

## Best Practices

### 1. Monitoring Frequency
- **Real-time**: Dashboard updates every 5 minutes
- **Scheduled**: Automated checks every 24 hours
- **On-demand**: Manual checks when needed

### 2. Threshold Management
- **Conservative**: Start with conservative thresholds
- **Gradual**: Adjust thresholds based on historical data
- **Context-aware**: Consider business context when setting thresholds

### 3. Retraining Strategy
- **Automated**: Enable auto-retraining for production
- **Validation**: Always validate retrained models
- **Rollback**: Maintain rollback capability
- **Backup**: Keep backups of all model versions

### 4. Alert Management
- **Prioritization**: Classify alerts by severity
- **Actionable**: Ensure all alerts are actionable
- **Noise Reduction**: Avoid alert fatigue
- **Documentation**: Document alert response procedures

## Troubleshooting

### Common Issues

1. **High False Positive Drift Detection**
   - Adjust drift_threshold in configuration
   - Increase minimum_samples_for_drift
   - Check data quality and preprocessing

2. **Frequent Retraining Triggers**
   - Review performance thresholds
   - Increase retrain_cooldown_hours
   - Investigate data quality issues

3. **Dashboard Not Loading**
   - Check Flask app configuration
   - Verify monitoring blueprint registration
   - Review logs for errors

4. **Notification Failures**
   - Verify webhook URLs and credentials
   - Check network connectivity
   - Review notification configuration

### Debugging Tips

```bash
# Check monitoring logs
tail -f logs/models.model_monitor.log

# Test monitoring components
python -c "from models.model_monitor import ModelMonitor; m = ModelMonitor(); print('OK')"

# Validate configuration
python -c "import json; print(json.load(open('config/model_config.json')))"

# Test API endpoints
curl http://localhost:5000/monitoring/api/summary
```

## Future Enhancements

### Planned Features
- **A/B Testing**: Support for model A/B testing
- **Model Versioning**: Enhanced model version management
- **Advanced Drift Detection**: More sophisticated drift detection methods
- **Automated Hyperparameter Tuning**: Auto-tune during retraining
- **Model Explainability**: Integration with model explanation tools
- **Custom Metrics**: Support for custom performance metrics

### Integration Ideas
- **MLflow Integration**: Model registry and experiment tracking
- **Prometheus/Grafana**: Advanced monitoring and alerting
- **Kubernetes**: Cloud-native deployment and monitoring
- **Apache Airflow**: Workflow orchestration
- **Data Version Control (DVC)**: Data and model versioning

## Contributing

When contributing to the monitoring system:

1. **Test Thoroughly**: Test all monitoring components
2. **Update Documentation**: Keep documentation current
3. **Follow Standards**: Maintain code quality standards
4. **Add Tests**: Include tests for new features
5. **Consider Performance**: Monitor system performance impact
