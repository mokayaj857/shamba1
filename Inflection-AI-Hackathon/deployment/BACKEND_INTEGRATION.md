# Backend Integration Guide for Agri-Adapt AI

This guide covers the complete backend integration for the maize yield prediction model, including FastAPI deployment, database setup, monitoring, and production deployment.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### 2. Start the Backend

```bash
# Development mode
python src/api/fastapi_app.py

# Production mode with uvicorn
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000/api

## 🏗️ Architecture Overview

### Components

1. **FastAPI Backend** (`src/api/fastapi_app.py`)

   - High-performance async API
   - Automatic OpenAPI documentation
   - Request validation with Pydantic
   - Background task processing

2. **Database Layer** (`src/api/database.py`)

   - SQLAlchemy ORM
   - PostgreSQL/SQLite support
   - Prediction storage and model versioning
   - Migration support with Alembic

3. **Monitoring System** (`src/api/monitoring.py`)

   - Real-time metrics collection
   - Prometheus integration
   - Performance tracking
   - Health monitoring

4. **Data Validation** (`src/api/schemas.py`)
   - Pydantic models for request/response
   - Input validation and sanitization
   - Type safety and documentation

### API Endpoints

| Endpoint                        | Method | Description                        |
| ------------------------------- | ------ | ---------------------------------- |
| `/`                             | GET    | API information and status         |
| `/health`                       | GET    | Health check with component status |
| `/docs`                         | GET    | Interactive API documentation      |
| `/api/counties`                 | GET    | List of Kenya counties             |
| `/api/predict`                  | POST   | Single prediction request          |
| `/api/predict/batch`            | POST   | Batch prediction requests          |
| `/api/model/status`             | GET    | Model training status              |
| `/api/model/feature-importance` | GET    | Feature importance scores          |
| `/api/metrics`                  | GET    | Application metrics                |

## 🗄️ Database Setup

### SQLite (Development)

```bash
# Default configuration uses SQLite
# Database file: agri_adapt_ai.db
python -c "from src.api.database import init_database; init_database()"
```

### PostgreSQL (Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE agri_adapt_ai;
CREATE USER agri_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agri_adapt_ai TO agri_user;
\q

# Set environment variable
export DATABASE_URL="postgresql://agri_user:secure_password@localhost/agri_adapt_ai"

# Initialize database
python -c "from src.api.database import init_database; init_database()"
```

### Database Models

- **PredictionRecord**: Stores all prediction requests and results
- **ModelVersion**: Tracks model versions and performance
- **TrainingRecord**: Records model training sessions
- **APIMetrics**: Stores API usage and performance metrics

## 📊 Monitoring and Metrics

### Built-in Metrics

The system automatically collects:

- **Prediction Metrics**: Request counts, success rates, processing times
- **Feature Metrics**: Input parameter distributions and statistics
- **Performance Metrics**: Response times, error rates, throughput
- **System Metrics**: Memory usage, uptime, health status

### Prometheus Integration

```bash
# Install Prometheus client
pip install prometheus-client

# Metrics endpoint: /metrics
# Prometheus format metrics available
```

### Custom Metrics

```python
from src.api.monitoring import get_metrics_collector

collector = get_metrics_collector()

# Record custom metrics
collector.record_prediction(
    rainfall=800.0,
    soil_ph=6.5,
    organic_carbon=2.1,
    resilience_score=75.5,
    processing_time=0.15
)
```

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **Performance Tests**: Response time validation
4. **Schema Tests**: Data validation testing

### Test Data

```python
# Sample prediction request
SAMPLE_PREDICTION_REQUEST = {
    "rainfall": 800.0,
    "soil_ph": 6.5,
    "organic_carbon": 2.1,
    "county": "Nakuru"
}
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build and start production services
docker-compose -f docker-compose.yml up -d

# Scale API service
docker-compose up -d --scale api=3

# Monitor services
docker-compose ps
docker-compose logs -f
```

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Model Configuration
MODEL_PATH=/app/models/maize_resilience_model.pkl
```

## 🔒 Security Considerations

### Production Security

1. **HTTPS**: Use Nginx with SSL certificates
2. **Authentication**: Implement API key or JWT authentication
3. **Rate Limiting**: Add request rate limiting
4. **Input Validation**: All inputs are validated with Pydantic
5. **SQL Injection**: Protected with SQLAlchemy ORM

### Environment Security

```bash
# Use environment variables for secrets
export DATABASE_PASSWORD="secure_password"
export API_SECRET_KEY="your_secret_key"

# Never commit secrets to version control
echo "*.env" >> .gitignore
```

## 📈 Performance Optimization

### API Performance

- **Async Processing**: FastAPI provides async request handling
- **Background Tasks**: Heavy operations run in background
- **Connection Pooling**: Database connection pooling
- **Caching**: Redis integration for caching

### Scaling Strategies

1. **Horizontal Scaling**: Multiple API instances behind load balancer
2. **Database Scaling**: Read replicas for heavy read workloads
3. **Caching**: Redis for frequently accessed data
4. **CDN**: Static content delivery optimization

## 🔍 Troubleshooting

### Common Issues

1. **Model Not Trained**

   ```bash
   # Check model status
   curl http://localhost:8000/api/model/status

   # Train the model first
   python scripts/train_model.py
   ```

2. **Database Connection Issues**

   ```bash
   # Check database health
   curl http://localhost:8000/health

   # Verify database connection
   python -c "from src.api.database import check_database_health; print(check_database_health())"
   ```

3. **Performance Issues**

   ```bash
   # Check metrics
   curl http://localhost:8000/api/metrics

   # Monitor response times
   curl -w "@curl-format.txt" http://localhost:8000/health
   ```

### Logs and Debugging

```bash
# View application logs
tail -f logs/app.log

# Enable debug logging
export LOG_LEVEL=DEBUG

# Check system resources
docker stats
```

## 🚀 Production Deployment

### Load Balancer Configuration (Nginx)

```nginx
upstream api_backend {
    server api:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring Stack

1. **Prometheus**: Metrics collection
2. **Grafana**: Visualization and dashboards
3. **AlertManager**: Alerting and notifications
4. **Node Exporter**: System metrics

### Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U username agri_adapt_ai > backup.sql

# Model backup
cp models/maize_resilience_model.pkl backup/

# Configuration backup
tar -czf config_backup.tar.gz config/
```

## 📚 API Usage Examples

### Python Client

```python
import requests
import json

# Single prediction
response = requests.post(
    "http://localhost:8000/api/predict",
    json={
        "rainfall": 800.0,
        "soil_ph": 6.5,
        "organic_carbon": 2.1,
        "county": "Nakuru"
    }
)

prediction = response.json()
print(f"Resilience Score: {prediction['prediction']['resilience_score']}%")

# Batch prediction
batch_response = requests.post(
    "http://localhost:8000/api/predict/batch",
    json={
        "predictions": [
            {"rainfall": 800.0, "soil_ph": 6.5, "organic_carbon": 2.1},
            {"rainfall": 900.0, "soil_ph": 7.0, "organic_carbon": 2.5}
        ]
    }
)

batch_results = batch_response.json()
print(f"Processed: {batch_results['total_processed']} predictions")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Get counties
curl http://localhost:8000/api/counties

# Make prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "rainfall": 800.0,
    "soil_ph": 6.5,
    "organic_carbon": 2.1,
    "county": "Nakuru"
  }'

# Get metrics
curl http://localhost:8000/api/metrics
```

## 🔄 Model Updates

### Model Versioning

```python
# Check current model version
curl http://localhost:8000/api/model/status

# Update model (requires retraining)
python scripts/retrain_model.py

# Activate new model version
python scripts/activate_model.py --version 2.1.0
```

### A/B Testing

```python
# Implement model routing based on version
# This can be done in the prediction endpoint
if model_version == "2.1.0":
    result = new_model.predict(input_data)
else:
    result = current_model.predict(input_data)
```

## 📞 Support and Maintenance

### Regular Maintenance

1. **Database Maintenance**: Weekly vacuum and analyze
2. **Log Rotation**: Daily log rotation and cleanup
3. **Backup Verification**: Weekly backup restoration tests
4. **Performance Monitoring**: Daily performance metrics review

### Monitoring Alerts

- High error rates (>5%)
- Slow response times (>2s p95)
- Database connection issues
- Model prediction failures

### Contact Information

- **Documentation**: [Project README](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Support**: support@agri-adapt-ai.com

---

This backend integration provides a robust, scalable, and production-ready system for your maize yield prediction model. The system is designed to handle high traffic, provide comprehensive monitoring, and maintain high availability.
