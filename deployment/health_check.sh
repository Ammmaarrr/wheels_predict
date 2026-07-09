#!/bin/bash

# Production Health Check Script
# This script checks the health of all services

set -e

echo "=========================================="
echo "PakWheels Production Health Check"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Docker containers are running
echo "Checking Docker containers..."
if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    print_success "Docker containers are running"
else
    print_error "Some Docker containers are not running"
    docker-compose -f docker-compose.production.yml ps
fi

# Check FastAPI health
echo "Checking FastAPI backend..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "FastAPI backend is healthy"
else
    print_error "FastAPI backend is not responding"
fi

# Check Frontend health
echo "Checking React frontend..."
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    print_success "React frontend is healthy"
else
    print_error "React frontend is not responding"
fi

# Check Database connection
echo "Checking database connection..."
if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U pakwheels_user > /dev/null 2>&1; then
    print_success "Database is connected"
else
    print_error "Database connection failed"
fi

# Check Redis connection
echo "Checking Redis connection..."
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis is connected"
else
    print_error "Redis connection failed"
fi

# Check Nginx
echo "Checking Nginx..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "Nginx is healthy"
else
    print_error "Nginx is not responding"
fi

# Check disk space
echo "Checking disk space..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Disk usage is normal ($DISK_USAGE%)"
else
    print_warning "Disk usage is high ($DISK_USAGE%)"
fi

# Check memory usage
echo "Checking memory usage..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    print_success "Memory usage is normal ($MEMORY_USAGE%)"
else
    print_warning "Memory usage is high ($MEMORY_USAGE%)"
fi

# Check API endpoints
echo "Checking API endpoints..."
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "API endpoints are accessible"
else
    print_error "API endpoints are not accessible"
fi

# Check SSL certificate (if HTTPS is enabled)
if [ -f "deployment/ssl/cert.pem" ]; then
    echo "Checking SSL certificate..."
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in deployment/ssl/cert.pem | cut -d= -f2)
    CERT_EXPIRY_TIMESTAMP=$(date -d "$CERT_EXPIRY" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( ($CERT_EXPIRY_TIMESTAMP - $CURRENT_TIMESTAMP) / 86400 ))
    
    if [ "$DAYS_UNTIL_EXPIRY" -gt 30 ]; then
        print_success "SSL certificate is valid ($DAYS_UNTIL_EXPIRY days remaining)"
    else
        print_warning "SSL certificate expires soon ($DAYS_UNTIL_EXPIRY days remaining)"
    fi
fi

# Check log files for errors
echo "Checking recent errors in logs..."
ERROR_COUNT=$(docker-compose -f docker-compose.production.yml logs --since="1h" | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "No errors found in recent logs"
else
    print_warning "Found $ERROR_COUNT errors in recent logs"
fi

# Performance check
echo "Checking API response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:8000/health)
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    print_success "API response time is good (${RESPONSE_TIME}s)"
else
    print_warning "API response time is slow (${RESPONSE_TIME}s)"
fi

echo ""
echo "=========================================="
echo "Health Check Summary"
echo "=========================================="
echo "Timestamp: $(date)"
echo "Status: All critical services checked"
echo ""
echo "For detailed monitoring, visit:"
echo "📊 Grafana: http://localhost:3001"
echo "📈 Prometheus: http://localhost:9090"
echo ""
