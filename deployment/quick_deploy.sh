#!/bin/bash

# Quick Production Deployment Script for PakWheels
# This script provides a streamlined deployment process

echo "=========================================="
echo "PakWheels Quick Production Deployment"
echo "=========================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "This script is designed for Linux systems"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. Please log out and log back in, then run this script again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Setup environment
echo "Setting up environment..."
if [ ! -f ".env.production" ]; then
    cp .env.production.example .env.production
    echo "Please edit .env.production with your settings"
    read -p "Press Enter to continue after editing..."
fi

# Create SSL directory
mkdir -p deployment/ssl

# Generate self-signed certificate for testing
if [ ! -f "deployment/ssl/cert.pem" ]; then
    echo "Generating SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout deployment/ssl/key.pem \
        -out deployment/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=PakWheels/CN=localhost"
fi

# Build and start services
echo "Building and starting services..."
docker-compose -f docker-compose.production.yml up -d --build

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Health checks
echo "Running health checks..."
docker-compose -f docker-compose.production.yml ps

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "🌐 Application: http://localhost"
echo "🔧 API: http://localhost/api"
echo "📊 Monitoring: http://localhost:3001"
echo ""
echo "Next steps:"
echo "1. Configure your domain name"
echo "2. Set up SSL certificate with Let's Encrypt"
echo "3. Configure monitoring alerts"
echo ""
echo "Useful commands:"
echo "  docker-compose -f docker-compose.production.yml logs -f"
echo "  docker-compose -f docker-compose.production.yml restart"
echo "  docker-compose -f docker-compose.production.yml down"
echo ""
