# Windows PowerShell Deployment Script for PakWheels
# This script provides deployment commands for Windows environment

Write-Host "=========================================="
Write-Host "PakWheels Windows Deployment Script"
Write-Host "=========================================="

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Please install Docker Desktop for Windows first." -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not available. Please install Docker Desktop." -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
}

# Create necessary directories
$directories = @("deployment\ssl", "logs", "data\cleaned", "models")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Yellow
    }
}

# Check if environment file exists
if (-not (Test-Path ".env.production")) {
    Write-Host "❌ .env.production file not found. Creating from template..." -ForegroundColor Red
    Copy-Item ".env.production.example" ".env.production" -Force
    Write-Host "✅ Created .env.production file" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env.production with your settings before continuing" -ForegroundColor Yellow
    notepad.exe .env.production
    Read-Host "Press Enter to continue after editing the file"
}

# Generate SSL certificate for local development
if (-not (Test-Path "deployment\ssl\cert.pem")) {
    Write-Host "Generating self-signed SSL certificate..." -ForegroundColor Yellow
    
    # Create OpenSSL configuration
    $opensslConfig = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = PakWheels
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
"@
    
    $opensslConfig | Out-File -FilePath "deployment\ssl\openssl.conf" -Encoding ASCII
    
    # Check if OpenSSL is available
    if (Get-Command openssl -ErrorAction SilentlyContinue) {
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "deployment\ssl\key.pem" -out "deployment\ssl\cert.pem" -config "deployment\ssl\openssl.conf"
        Write-Host "✅ SSL certificate generated" -ForegroundColor Green
    } else {
        Write-Host "⚠️  OpenSSL not found. Using basic certificate generation..." -ForegroundColor Yellow
        # Create dummy certificate files for development
        "-----BEGIN CERTIFICATE-----" | Out-File -FilePath "deployment\ssl\cert.pem" -Encoding ASCII
        "-----BEGIN PRIVATE KEY-----" | Out-File -FilePath "deployment\ssl\key.pem" -Encoding ASCII
    }
}

# Build and start services
Write-Host "Building Docker containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml build

Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml ps

# Health checks
Write-Host "Running health checks..." -ForegroundColor Yellow

# Check FastAPI
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ FastAPI backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FastAPI backend health check failed" -ForegroundColor Red
}

# Check Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ React frontend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ React frontend health check failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Deployment Complete!"
Write-Host "=========================================="
Write-Host "🌐 Application: http://localhost" -ForegroundColor Green
Write-Host "🔧 API: http://localhost:8000" -ForegroundColor Green
Write-Host "📊 Monitoring: http://localhost:3001" -ForegroundColor Green
Write-Host "📈 Metrics: http://localhost:9090" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose -f docker-compose.production.yml logs -f"
Write-Host "  Restart: docker-compose -f docker-compose.production.yml restart"
Write-Host "  Stop: docker-compose -f docker-compose.production.yml down"
Write-Host "  Update: docker-compose -f docker-compose.production.yml up -d --build"
Write-Host ""
Write-Host "🚀 PakWheels is now running in production mode!" -ForegroundColor Green
