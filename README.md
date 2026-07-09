# Wheels Predict

## Project Overview
This project provides an end-to-end pipeline for scraping car listings, cleaning and processing the data, training machine learning models for price prediction, and serving recommendations via a web interface.

## Architecture
- **scrapers/**: Scrapy spiders and scripts for data collection
- **data_processing/**: Data cleaning and preprocessing scripts
- **models/**: Model training, inference, and saved models
- **web/**: Flask web interface and HTML templates
- **database/**: Database utilities and SQL scripts
- **notebooks/**: Jupyter notebooks for analysis and prototyping
- **config/**: Configuration files and requirements
- **tests/**: Unit and integration tests
- **deployment/**: (Planned) Docker, CI/CD, and deployment scripts

## Data Flow
1. **Scraping**: Use Scrapy spiders in `scrapers/` to collect car listings from Wheels Predict.
2. **Processing**: Clean and preprocess raw data using scripts in `data_processing/`.
3. **Modeling**: Train and tune ML models in `models/`.
4. **Serving**: Serve predictions and recommendations via the Flask app in `web/`.
5. **Database**: Store and retrieve data using utilities in `database/`.

## Setup Instructions
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   ```
3. Configure environment variables (see `.env.example`).
4. Run scrapers and data processing scripts as needed.
5. Start the web interface:
   ```bash
   python web/web_interface.py
   ```

## Usage
- To scrape data: Run scripts in `scrapers/`.
- To preprocess data: Use scripts in `data_processing/`.
- To train models: Use scripts in `models/`.
- To launch the web app: See above.

## Contribution
Pull requests are welcome! Please add tests for new features and update documentation as needed.

## License
[MIT](LICENSE)

## Docker Setup
The project is containerized using Docker for easy deployment and reproducibility.

### Prerequisites
- Docker
- Docker Compose

### Running with Docker
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the services:
   - Web Interface: http://localhost:5000
   - Jupyter Notebook: http://localhost:8888

3. Stop the containers:
   ```bash
   docker-compose down
   ```

### Docker Services
- **web**: Flask web interface for predictions and recommendations
- **scraper**: Automated scraping service running on a schedule
- **notebook**: Jupyter notebook service for analysis and development

### Environment Variables
Docker uses `.env` for configuration. Copy `.env.example` to `.env` and modify:
```bash
cp .env.example .env
# Edit .env with your settings
```

### Data Persistence
Docker mounts these directories for data persistence:
- `./data`: Raw and processed data
- `./logs`: Application logs
- `./models`: Trained models
- `./notebooks`: Jupyter notebooks

### Development with Docker
1. Make code changes in your local environment
2. Docker will sync changes with containers via volumes
3. Restart services to apply changes:
   ```bash
   docker-compose restart [service_name]
   ```

### Production Deployment
For production:
1. Set `FLASK_ENV=production` in `.env`
2. Set secure `JUPYTER_TOKEN` in `.env`
3. Use proper SSL/TLS certificates
4. Configure proper authentication
5. Use production-grade servers (e.g., Gunicorn)

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment.

### Workflows

1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
   - Runs on push to `main` and `develop` branches
   - Executes tests across multiple Python versions
   - Performs security scans
   - Builds and tests Docker images
   - Deploys to staging/production environments

2. **Scheduled Data Scraping** (`.github/workflows/scheduled-scraping.yml`)
   - Runs daily at 2 AM UTC
   - Automatically scrapes new data
   - Processes and cleans the data
   - Updates ML models if needed
   - Commits changes back to repository

3. **Code Quality Checks** (`.github/workflows/code-quality.yml`)
   - Runs on every push and pull request
   - Checks code formatting (Black, isort)
   - Performs linting (flake8, pylint)
   - Type checking (mypy)
   - Security analysis (Bandit)
   - Complexity analysis

4. **Dependency Updates** (`.github/workflows/dependency-updates.yml`)
   - Runs weekly on Sundays
   - Updates Python dependencies
   - Creates pull requests for review
   - Performs security audits

5. **Production Deployment** (`.github/workflows/deployment.yml`)
   - Triggered on releases or manual dispatch
   - Builds multi-platform Docker images
   - Deploys to staging/production
   - Runs health checks and smoke tests

### Branch Strategy

- **`main`**: Production branch, auto-deploys to production
- **`develop`**: Development branch, auto-deploys to staging
- **Feature branches**: Create from `develop`, merge via pull requests

### Required Secrets

Configure these secrets in your GitHub repository:

```bash
# Docker Registry (if using external registry)
DOCKER_REGISTRY=ghcr.io
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_token

# Deployment (configure based on your infrastructure)
DEPLOY_HOST=your_server
DEPLOY_USER=deploy_user
DEPLOY_KEY=your_ssh_key

# Notifications (optional)
SLACK_WEBHOOK_URL=your_slack_webhook
TEAMS_WEBHOOK_URL=your_teams_webhook
```

### Local Development

Run quality checks locally before pushing:

```bash
# Install development dependencies
pip install -r tests/requirements_test.txt

# Format code
black .
isort .

# Run linting
flake8 .
pylint $(find . -name "*.py" | head -10)

# Type checking
mypy . --ignore-missing-imports

# Security scan
bandit -r .

# Run tests
pytest tests/ -v --cov=.
```

### Code Quality Standards

- **Code Coverage**: Minimum 80% coverage required
- **Complexity**: Maximum cyclomatic complexity of 10
- **Security**: No high-severity security issues
- **Style**: Black formatting with 88-character line limit
- **Documentation**: All public functions must have docstrings

### Deployment Environments

- **Staging**: Automatic deployment from `develop` branch
  - URL: https://wheelspredict-staging.yourdomain.com
  - Database: Staging database with subset of data
  - Monitoring: Basic health checks

- **Production**: Automatic deployment from `main` branch
  - URL: https://wheelspredict.yourdomain.com
  - Database: Production database
  - Monitoring: Full monitoring and alerting

### Manual Deployment

To manually trigger deployment:

```bash
# Deploy to staging
gh workflow run deployment.yml -f environment=staging

# Deploy to production
gh workflow run deployment.yml -f environment=production
```

## Model Monitoring and Retraining

The project includes a comprehensive model monitoring and automated retraining system to ensure optimal model performance in production.

### Key Features

- **Real-time Performance Monitoring**: Continuous tracking of model metrics (MAE, RMSE, R²)
- **Data Drift Detection**: Statistical analysis to detect changes in data distribution
- **Automated Retraining**: Intelligent retraining triggers based on performance degradation
- **Interactive Dashboard**: Web-based monitoring dashboard with visualizations
- **Alert System**: Configurable alerts for performance issues and drift detection
- **CI/CD Integration**: Automated monitoring and retraining via GitHub Actions

### Monitoring Dashboard

Access the monitoring dashboard at `http://localhost:5000/monitoring/dashboard` when running the web interface.

The dashboard provides:
- **Model Performance Overview**: Real-time metrics for all models
- **Performance Trends**: Historical performance visualization
- **Data Drift Analysis**: Feature-level drift detection
- **Retraining Management**: Manual and automated retraining controls
- **Alert Management**: Active alerts and notifications

### Automated Monitoring Workflow

The system runs automated monitoring checks:

1. **Daily Scheduled Checks**: GitHub Actions workflow runs at 3 AM UTC
2. **Performance Evaluation**: Checks all models against baseline metrics
3. **Drift Detection**: Analyzes recent data for distribution changes
4. **Automatic Retraining**: Triggers retraining when thresholds are exceeded
5. **Notification Alerts**: Sends alerts via Slack, Teams, or email
6. **Model Updates**: Commits retrained models back to repository

### Configuration

Model monitoring is configured via `config/model_config.json`:

```json
{
  "thresholds": {
    "mae_threshold": 500000,
    "rmse_threshold": 1000000,
    "r2_threshold": 0.7,
    "performance_degradation": 0.1
  },
  "monitoring": {
    "check_interval_hours": 24
  },
  "retraining": {
    "auto_retrain": true,
    "backup_old_models": true
  }
}
```

### Manual Monitoring Commands

```bash
# Check which models need retraining
python scripts/retrain_models.py --dry-run

# Retrain specific model
python scripts/retrain_models.py --model xgb_model_updated

# Force retrain all models with notifications
python scripts/retrain_models.py --force --notify

# Run full monitoring check
python scripts/retrain_models.py --notify
```

### API Endpoints

The monitoring system provides REST API endpoints:

- `GET /monitoring/api/metrics/all` - All model performance metrics
- `GET /monitoring/api/drift/{model_name}` - Data drift analysis
- `POST /monitoring/api/retrain/{model_name}` - Trigger model retraining
- `GET /monitoring/api/alerts` - Current system alerts
- `GET /monitoring/api/summary` - Monitoring dashboard summary

For detailed monitoring documentation, see [`monitoring/README.md`](monitoring/README.md).

## Step 8: Model Monitoring and Retraining Pipeline ✅ COMPLETED

### Implementation Summary

I've successfully implemented a comprehensive model monitoring and automated retraining system for your Wheels Predict pipeline:

#### 🔍 **Core Monitoring Components**

1. **Model Performance Monitor** (`models/model_monitor.py`)
   - Real-time performance tracking (MAE, RMSE, R², MAPE)
   - Configurable performance thresholds
   - Baseline metrics management
   - Historical performance logging

2. **Data Drift Detection**
   - Statistical tests for numerical features (Kolmogorov-Smirnov)
   - Chi-square tests for categorical features
   - Configurable drift sensitivity thresholds
   - Feature-level drift analysis

3. **Automated Retraining Pipeline**
   - Performance-based retraining triggers
   - Drift-based retraining decisions
   - Scheduled monitoring checks
   - Backup and rollback capabilities

#### 🖥️ **Web Dashboard & API**

1. **Interactive Monitoring Dashboard** (`web/templates/monitoring_dashboard.html`)
   - Real-time performance metrics display
   - Historical trend visualizations
   - Alert management interface
   - Manual retraining triggers

2. **REST API Endpoints** (`models/monitoring_api.py`)
   - `/monitoring/api/metrics/all` - All model metrics
   - `/monitoring/api/drift/{model_name}` - Drift analysis
   - `/monitoring/api/retrain/{model_name}` - Trigger retraining
   - `/monitoring/api/alerts` - System alerts
   - `/monitoring/api/summary` - Dashboard summary

#### 🤖 **Automated Workflows**

1. **GitHub Actions Integration** (`.github/workflows/model-monitoring.yml`)
   - Daily scheduled monitoring at 3 AM UTC
   - Automated retraining when thresholds exceeded
   - GitHub issue creation for failures
   - Multi-channel notifications (Slack, Teams)

2. **Command Line Interface** (`scripts/retrain_models.py`)
   - Dry-run mode for testing
   - Force retraining option
   - Configurable notifications
   - Detailed logging and reporting

#### ⚙️ **Configuration Management**

1. **Model Configuration** (`config/model_config.json`)
   - Performance thresholds
   - Monitoring intervals
   - Retraining policies
   - Notification settings

2. **Environment Variables Support**
   - Secure credential management
   - Flexible deployment configuration
   - Production/staging separation

#### 🧪 **Testing & Validation**

1. **Comprehensive Test Suite** (`tests/test_model_monitoring.py`)
   - Unit tests for all monitoring components
   - Integration tests for end-to-end workflows
   - Mock testing for retraining scenarios
   - All 16 tests passing successfully

#### 📊 **Key Features**

- **Real-time Monitoring**: Continuous performance tracking
- **Intelligent Alerts**: Configurable thresholds and notifications
- **Automated Retraining**: Self-healing ML pipeline
- **Historical Analysis**: Long-term performance trends
- **Web Interface**: User-friendly monitoring dashboard
- **API Integration**: RESTful endpoints for external integration
- **CI/CD Integration**: Automated monitoring workflows
- **Comprehensive Logging**: Detailed audit trails

#### 🚀 **Usage Examples**

```bash
# Check model performance
python scripts/retrain_models.py --dry-run

# Monitor specific model
python scripts/retrain_models.py --model xgb_model_updated

# Force retrain with notifications
python scripts/retrain_models.py --force --notify

# Access monitoring dashboard
# Start web app: python web/web_interface.py
# Visit: http://localhost:5000/monitoring/dashboard
```

#### 📈 **Benefits**

1. **Proactive Monitoring**: Detect issues before they impact users
2. **Automated Maintenance**: Reduce manual intervention
3. **Quality Assurance**: Maintain model performance over time
4. **Operational Insights**: Comprehensive monitoring data
5. **Scalable Architecture**: Easy to extend and customize

The monitoring system is now fully operational and integrated with your existing CI/CD pipeline, providing enterprise-grade ML operations capabilities for your PakWheels project.
