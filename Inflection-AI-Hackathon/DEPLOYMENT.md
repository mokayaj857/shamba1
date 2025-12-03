# 🚀 Deployment Guide

This guide covers deploying Agri-Adapt AI to various environments, from local development to production cloud platforms.

---

## 🏠 Local Development

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git
- Virtual environment tools

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/agri-adapt-ai.git
cd agri-adapt-ai

# Backend setup
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Start services
python scripts/start_backend.py &  # Backend on :8000
cd frontend && npm run dev &        # Frontend on :3000
```

---

## 🐳 Docker Deployment

### Single Container Deployment

#### Backend Only

```bash
# Build backend image
docker build -t agri-adapt-ai-backend .

# Run backend container
docker run -d \
  --name agri-adapt-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=False \
  agri-adapt-ai-backend
```

#### Frontend Only

```bash
cd frontend

# Build frontend image
docker build -t agri-adapt-ai-frontend .

# Run frontend container
docker run -d \
  --name agri-adapt-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  agri-adapt-ai-frontend
```

### Multi-Container with Docker Compose

#### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  backend:
    build: .
    container_name: agri-adapt-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: agri-adapt-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=production
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: agri-adapt-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  data:
  logs:
```

#### Development Docker Compose

```yaml
# docker-compose.dev.yml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: agri-adapt-backend-dev
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=True
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app
      - ./data:/app/data
    command: python scripts/start_backend.py --reload
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: agri-adapt-frontend-dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    restart: unless-stopped
```

### Docker Commands

#### Build and Run

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Clean up
docker-compose -f docker-compose.prod.yml down -v --rmi all
```

#### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View development logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml build --no-cache

# Access container shell
docker exec -it agri-adapt-backend-dev bash
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Instance type: t3.medium or larger
# Security group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-username/agri-adapt-ai.git
cd agri-adapt-ai

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

#### AWS ECS Deployment

```yaml
# task-definition.json
{
  "family": "agri-adapt-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions":
    [
      {
        "name": "backend",
        "image": "your-account.dkr.ecr.region.amazonaws.com/agri-adapt-backend:latest",
        "portMappings": [{ "containerPort": 8000, "protocol": "tcp" }],
        "environment": [{ "name": "ENVIRONMENT", "value": "production" }],
        "logConfiguration":
          {
            "logDriver": "awslogs",
            "options":
              {
                "awslogs-group": "/ecs/agri-adapt-ai",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs",
              },
          },
      },
    ],
}
```

### Google Cloud Platform

#### GKE Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agri-adapt-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agri-adapt-backend
  template:
    metadata:
      labels:
        app: agri-adapt-backend
    spec:
      containers:
        - name: backend
          image: gcr.io/your-project/agri-adapt-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "production"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: agri-adapt-backend-service
spec:
  selector:
    app: agri-adapt-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Azure Deployment

#### Azure Container Instances

```bash
# Create resource group
az group create --name agri-adapt-ai --location eastus

# Create container instance
az container create \
  --resource-group agri-adapt-ai \
  --name agri-adapt-backend \
  --image your-registry.azurecr.io/agri-adapt-backend:latest \
  --dns-name-label agri-adapt-backend \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production DEBUG=False

# Create frontend container
az container create \
  --resource-group agri-adapt-ai \
  --name agri-adapt-frontend \
  --image your-registry.azurecr.io/agri-adapt-frontend:latest \
  --dns-name-label agri-adapt-frontend \
  --ports 3000 \
  --environment-variables NEXT_PUBLIC_API_URL=http://agri-adapt-backend.eastus.azurecontainer.io:8000
```

---

## 🌐 Production Setup

### Environment Configuration

#### Backend Environment Variables

```bash
# .env.production
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security
SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=100

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_TO_FILE=True
LOG_FILE_PATH=/app/logs/backend.log

# External Services
WEATHER_API_KEY=your-weather-api-key
SOIL_DATA_API_KEY=your-soil-data-api-key
```

#### Frontend Environment Variables

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=Agri-Adapt AI
NEXT_PUBLIC_GA_TRACKING_ID=GA-XXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn

# Build optimization
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

### Reverse Proxy Configuration

#### Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            limit_req zone=web burst=50 nodelay;
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### SSL Certificate Setup

#### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoring and Logging

### Application Monitoring

#### Health Checks

```python
# src/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint."""
    try:
        # Database health
        db.execute("SELECT 1")

        # Model health
        # Add model loading check here

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.2.0",
            "services": {
                "database": "healthy",
                "ml_model": "healthy",
                "weather_api": "healthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### Metrics Collection

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Business metrics
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')
PREDICTION_ACCURACY = Gauge('prediction_accuracy', 'Model prediction accuracy')

# System metrics
MODEL_LOAD_TIME = Gauge('model_load_time_seconds', 'Time taken to load ML model')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
```

### Logging Configuration

#### Structured Logging

```python
# src/utils/logging.py
import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

# Configure logging
def setup_logging(level: str = "INFO", log_file: str = None):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

#### Backend CI/CD

```yaml
# .github/workflows/backend.yml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths: ["src/**", "requirements.txt", "Dockerfile"]
  pull_request:
    branches: [main, develop]
    paths: ["src/**", "requirements.txt", "Dockerfile"]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black

      - name: Lint code
        run: |
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check src/

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t agri-adapt-backend:${{ github.sha }} .
          docker tag agri-adapt-backend:${{ github.sha }} agri-adapt-backend:latest

      - name: Deploy to production
        run: |
          # Add your deployment commands here
          echo "Deploying to production..."
```

#### Frontend CI/CD

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main, develop]
    paths: ["frontend/**"]
  pull_request:
    branches: [main, develop]
    paths: ["frontend/**"]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "16"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

      - name: Build application
        run: |
          cd frontend
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: "--prod"
```

---

## 🚨 Troubleshooting

### Common Deployment Issues

#### Port Conflicts

```bash
# Check what's using a port
sudo netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 <PID>

# Alternative: Use different port
export PORT=8001
```

#### Docker Issues

```bash
# Check container status
docker ps -a

# View container logs
docker logs <container-name>

# Restart container
docker restart <container-name>

# Rebuild container
docker-compose build --no-cache <service-name>
```

#### Database Connection Issues

```bash
# Test database connection
python -c "
from src.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"

# Check database file permissions
ls -la agri_adapt_ai.db
chmod 644 agri_adapt_ai.db
```

### Performance Optimization

#### Backend Optimization

```python
# Enable async processing
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

@app.post("/api/predict/batch")
async def batch_predict(predictions: List[PredictionInput]):
    """Process multiple predictions concurrently."""
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(executor, process_prediction, pred)
        for pred in predictions
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### Frontend Optimization

```typescript
// Enable code splitting
import dynamic from "next/dynamic";

const ResilienceGauge = dynamic(() => import("./ResilienceGauge"), {
  loading: () => <div>Loading...</div>,
  ssr: false,
});

// Optimize images
import Image from "next/image";

<Image
  src="/placeholder-logo.png"
  alt="Logo"
  width={200}
  height={100}
  priority
/>;
```

---

## 📚 Additional Resources

### Documentation

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)

### Tools

- [Docker Compose](https://docs.docker.com/compose/)
- [Nginx](https://nginx.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

---

## 🎯 Next Steps

After successful deployment:

1. **Set up monitoring** with Prometheus and Grafana
2. **Configure backups** for database and configuration files
3. **Implement CI/CD** for automated deployments
4. **Set up SSL certificates** for HTTPS
5. **Configure logging** aggregation and analysis
6. **Set up alerting** for critical issues
7. **Plan scaling** strategy for increased load

---

**Happy Deploying! 🚀**

For deployment support, create an issue in the GitHub repository or contact the development team.

---

**Last Updated**: December 2024  
**Maintainer**: [Your Name]
