#!/bin/bash

# PakWheels Production Deployment Script
# This script automates the deployment process

set -e

echo "=========================================="
echo "PakWheels Production Deployment Script"
echo "=========================================="

# Configuration
DOMAIN="${DOMAIN:-pakwheels.local}"
EMAIL="${EMAIL:-admin@pakwheels.local}"
BRANCH="${BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Starting deployment process..."

# Step 1: Update system packages
print_status "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Step 2: Install required packages
print_status "Installing required packages..."
sudo apt-get install -y curl wget git nginx certbot python3-certbot-nginx

# Step 3: Clone or update repository
if [ -d "/opt/pakwheels" ]; then
    print_status "Updating existing repository..."
    cd /opt/pakwheels
    git pull origin $BRANCH
else
    print_status "Cloning repository..."
    sudo git clone https://github.com/yourusername/pakwheels.git /opt/pakwheels
    sudo chown -R $USER:$USER /opt/pakwheels
    cd /opt/pakwheels
fi

# Step 4: Setup environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env.production" ]; then
    cp .env.production.example .env.production
    print_warning "Please edit .env.production file with your configuration before continuing"
    read -p "Press Enter to continue after editing the file..."
fi

# Step 5: Generate SSL certificates
print_status "Setting up SSL certificates..."
if [ ! -f "deployment/ssl/cert.pem" ]; then
    mkdir -p deployment/ssl
    
    # Generate self-signed certificate for development
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout deployment/ssl/key.pem \
        -out deployment/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    print_warning "Self-signed certificate created. For production, use Let's Encrypt:"
    print_warning "sudo certbot --nginx -d $DOMAIN"
fi

# Step 6: Build and start containers
print_status "Building Docker containers..."
docker-compose -f docker-compose.production.yml build --no-cache

print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Step 7: Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Step 8: Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T fastapi python -c "
import asyncio
from sqlalchemy import create_engine
from database.db_utils import create_tables

async def main():
    try:
        create_tables()
        print('Database tables created successfully')
    except Exception as e:
        print(f'Error creating tables: {e}')

asyncio.run(main())
"

# Step 9: Load initial data
print_status "Loading initial data..."
docker-compose -f docker-compose.production.yml exec -T fastapi python -c "
import pandas as pd
from pathlib import Path

# Check if data files exist
data_dir = Path('data/cleaned')
if data_dir.exists():
    csv_files = list(data_dir.glob('*.csv'))
    if csv_files:
        print(f'Found {len(csv_files)} data files')
        # Load latest data file
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        df = pd.read_csv(latest_file)
        print(f'Loaded {len(df)} records from {latest_file.name}')
    else:
        print('No data files found')
else:
    print('Data directory not found')
"

# Step 10: Health checks
print_status "Running health checks..."

# Check FastAPI
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ FastAPI backend is healthy"
else
    print_error "❌ FastAPI backend health check failed"
fi

# Check Frontend
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    print_status "✅ React frontend is healthy"
else
    print_error "❌ React frontend health check failed"
fi

# Check Database
if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U pakwheels_user > /dev/null 2>&1; then
    print_status "✅ Database is healthy"
else
    print_error "❌ Database health check failed"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis is healthy"
else
    print_error "❌ Redis health check failed"
fi

# Step 11: Setup monitoring
print_status "Setting up monitoring..."
docker-compose -f docker-compose.production.yml exec -T prometheus wget -q --spider http://localhost:9090 && \
print_status "✅ Prometheus is running on port 9090"

docker-compose -f docker-compose.production.yml exec -T grafana curl -f http://localhost:3000 > /dev/null 2>&1 && \
print_status "✅ Grafana is running on port 3001"

# Step 12: Display deployment information
print_status "Deployment completed successfully!"
echo ""
echo "=========================================="
echo "DEPLOYMENT INFORMATION"
echo "=========================================="
echo "🌐 Application URL: https://$DOMAIN"
echo "🔧 API URL: https://$DOMAIN/api"
echo "📊 Monitoring: http://$DOMAIN:3001 (Grafana)"
echo "📈 Metrics: http://$DOMAIN:9090 (Prometheus)"
echo ""
echo "Container Status:"
docker-compose -f docker-compose.production.yml ps
echo ""
echo "📋 Next Steps:"
echo "1. Update DNS records to point to this server"
echo "2. Configure SSL certificate with Let's Encrypt"
echo "3. Set up backup schedule"
echo "4. Configure monitoring alerts"
echo "5. Test all functionality"
echo ""
echo "🔍 Useful Commands:"
echo "  View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  Restart: docker-compose -f docker-compose.production.yml restart"
echo "  Stop: docker-compose -f docker-compose.production.yml down"
echo "  Update: git pull && docker-compose -f docker-compose.production.yml up -d --build"
echo ""
print_status "Deployment completed successfully! 🚀"
