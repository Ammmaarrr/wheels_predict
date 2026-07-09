# 🚀 PakWheels Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the PakWheels FastAPI + React application to a production server using Docker and modern DevOps practices.

## 🏗️ Architecture
```
Internet → Load Balancer (Nginx) → FastAPI Backend (Port 8000)
                                 → React Frontend (Port 3000)
                                 → PostgreSQL Database (Port 5432)
                                 → Redis Cache (Port 6379)
                                 → Monitoring (Prometheus/Grafana)
```

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04 LTS or newer
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB+ SSD
- **Network**: Static IP address

### Software Requirements
- Docker 24.0+
- Docker Compose 2.0+
- Git
- Nginx (for SSL termination)
- Certbot (for SSL certificates)

## 🔧 Installation Steps

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git nginx certbot python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Repository
```bash
# Clone to production directory
sudo git clone https://github.com/yourusername/pakwheels.git /opt/pakwheels
sudo chown -R $USER:$USER /opt/pakwheels
cd /opt/pakwheels
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.production.example .env.production

# Edit configuration (update with your values)
nano .env.production
```

### Step 4: SSL Certificate Setup
```bash
# Create SSL directory
mkdir -p deployment/ssl

# For development (self-signed)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout deployment/ssl/key.pem \
    -out deployment/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# For production (Let's Encrypt)
sudo certbot certonly --nginx -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/ssl/key.pem
```

### Step 5: Deploy Application
```bash
# Make deployment script executable
chmod +x deployment/deploy.sh

# Run deployment
./deployment/deploy.sh
```

### Step 6: Verify Deployment
```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# Run health checks
chmod +x deployment/health_check.sh
./deployment/health_check.sh
```

## 📊 Monitoring & Maintenance

### Health Checks
- **FastAPI**: https://yourdomain.com/api/health
- **Frontend**: https://yourdomain.com/health
- **Grafana**: http://yourdomain.com:3001
- **Prometheus**: http://yourdomain.com:9090

### Log Management
```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service logs
docker-compose -f docker-compose.production.yml logs -f fastapi
docker-compose -f docker-compose.production.yml logs -f frontend
```

### Backup Setup
```bash
# Make backup script executable
chmod +x deployment/backup.sh

# Run manual backup
./deployment/backup.sh

# Setup automated backup (crontab)
crontab -e
# Add: 0 2 * * * /opt/pakwheels/deployment/backup.sh
```

## 🔄 Updates & Maintenance

### Update Application
```bash
cd /opt/pakwheels
git pull origin main
docker-compose -f docker-compose.production.yml up -d --build
```

### Scale Services
```bash
# Scale FastAPI workers
docker-compose -f docker-compose.production.yml up -d --scale fastapi=3
```

## 🔒 Security Considerations

### Firewall Configuration
```bash
# Configure UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS Setup
- Use Let's Encrypt for production SSL certificates
- Configure automatic renewal
- Implement HSTS headers
- Use secure cipher suites

## 📈 Performance Optimization

### Nginx Tuning
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 10M;
```

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Restart services
docker-compose -f docker-compose.production.yml restart
```

#### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.production.yml exec db pg_isready

# Reset database
docker-compose -f docker-compose.production.yml down
docker volume rm pakwheels_postgres-data
docker-compose -f docker-compose.production.yml up -d
```

---

**✅ Your PakWheels application is now ready for production deployment!**
