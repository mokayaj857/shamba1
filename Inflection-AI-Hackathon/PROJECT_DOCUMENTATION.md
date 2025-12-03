# 📚 Agri-Adapt AI: Complete Project Documentation

## 🏗️ System Architecture Deep Dive

### Backend Architecture (FastAPI)

The backend is built using FastAPI, a modern Python web framework that provides:

- **Automatic API Documentation**: Interactive docs at `/docs`
- **Type Validation**: Pydantic models for request/response validation
- **Async Support**: High-performance async request handling
- **OpenAPI Standards**: RESTful API with OpenAPI 3.0 specification

#### Core Components

1. **FastAPI Application** (`src/api/fastapi_app.py`)

   - Main application entry point
   - Route definitions and middleware configuration
   - Error handling and validation

2. **Data Service** (`src/api/data_service.py`)

   - Data loading and preprocessing
   - Weather data integration
   - County data management

3. **ML Model Service** (`src/models/maize_resilience_model.py`)
   - Machine learning model wrapper
   - Feature engineering and preprocessing
   - Prediction pipeline

### Frontend Architecture (Next.js 15)

The frontend uses Next.js 15 with the App Router for:

- **Server-Side Rendering**: Improved SEO and performance
- **Static Generation**: Pre-built pages for faster loading
- **API Routes**: Built-in API endpoints
- **TypeScript**: Type-safe development

#### Core Components

1. **Dashboard** (`frontend/app/page.tsx`)

   - Main application interface
   - County selection and form inputs
   - Results display

2. **Resilience Gauge** (`frontend/components/resilience-gauge.tsx`)

   - Visual score representation
   - Color-coded risk levels
   - Interactive tooltips

3. **Weather Integration** (`frontend/components/weather-integration.tsx`)
   - Real-time weather data
   - Monthly weather charts
   - County-specific information

---

## 🧮 Machine Learning Model Details

### Model Architecture

**Algorithm**: Random Forest Regressor

- **Ensemble Method**: Combines multiple decision trees
- **Advantages**: Handles non-linear relationships, robust to outliers
- **Hyperparameters**: Optimized using grid search and cross-validation

### Feature Engineering

The model uses 14 numerical features:

#### User Input Features

1. **Rainfall (mm)**: Annual precipitation amount
2. **Soil pH**: Acidity/alkalinity (0-14 scale)
3. **Organic Carbon (%)**: Soil organic matter content

#### County-Specific Features (Automatically Loaded)

4. **Monthly Temperature Mean (°C)**: Average monthly temperatures
5. **Monthly Temperature Std (°C)**: Temperature variability
6. **Monthly Humidity Mean (%)**: Average monthly humidity
7. **Monthly Humidity Std (%)**: Humidity variability
8. **Monthly Precipitation Mean (mm)**: Average monthly rainfall
9. **Monthly Precipitation Std (mm)**: Rainfall variability
10. **Soil Clay Mean (%)**: Average clay content
11. **Soil Silt Mean (%)**: Average silt content
12. **Climate Variability Index**: Temperature and precipitation variation
13. **County Encoding**: One-hot encoded county identifiers

### Training Data

- **Source**: Historical data from 2019-2023
- **Coverage**: 20 Kenyan counties
- **Data Points**: ~2,400 training samples
- **Validation**: 5-fold cross-validation
- **Test Set**: 20% holdout for final evaluation

### Model Performance

- **R² Score**: 0.70 (70% variance explained)
- **Mean Absolute Error**: 0.15 tons/hectare
- **Root Mean Square Error**: 0.22 tons/hectare
- **Response Time**: <1 second per prediction

---

## 🔧 Development Setup

### Environment Requirements

#### Python Environment

```bash
# Python 3.9+ required
python --version

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Node.js Environment

```bash
# Node.js 16+ required
node --version

# Install frontend dependencies
cd frontend
npm install
```

### Database Setup

The system uses SQLite for development:

```bash
# Database will be created automatically on first run
# Location: agri_adapt_ai.db (excluded from git)
```

### Configuration

Environment variables can be set in `.env` file:

```bash
# Backend configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=True

# Frontend configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Agri-Adapt AI
```

---

## 🧪 Testing Strategy

### Backend Testing

#### Unit Tests

```bash
# Run all unit tests
python -m pytest tests/unit/

# Run specific test file
python -m pytest tests/unit/test_ml_model.py

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

#### Integration Tests

```bash
# Run integration tests
python -m pytest tests/integration/

# Test API endpoints
python -m pytest tests/integration/test_api_endpoints.py
```

### Frontend Testing

#### Component Tests

```bash
cd frontend
# Run component tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test
npm test -- --testNamePattern="ResilienceGauge"
```

#### E2E Tests

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npx playwright test
```

---

## 🚀 Deployment Guide

### Production Environment

#### Backend Deployment

1. **Docker Deployment**

```bash
# Build image
docker build -t agri-adapt-ai-backend .

# Run container
docker run -d -p 8000:8000 --name agri-adapt-backend agri-adapt-ai-backend

# Using Docker Compose
docker-compose up -d
```

2. **Direct Deployment**

```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export ENVIRONMENT=production
export DEBUG=False

# Start with Gunicorn
gunicorn src.api.fastapi_app:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Frontend Deployment

1. **Build for Production**

```bash
cd frontend
npm run build
npm start
```

2. **Vercel Deployment**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

3. **Static Export**

```bash
# Export static files
npm run export

# Deploy to any static hosting service
```

### Environment Variables

#### Production Backend

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379
```

#### Production Frontend

```bash
NEXT_PUBLIC_API_URL=https://api.agri-adapt-ai.com
NEXT_PUBLIC_APP_NAME=Agri-Adapt AI
NEXT_PUBLIC_GA_TRACKING_ID=GA-XXXXXXXXX
```

---

## 📊 Data Pipeline

### Data Sources

1. **CHIRPS Rainfall Data**

   - Source: Climate Hazards Group InfraRed Precipitation with Station data
   - Format: NetCDF files
   - Resolution: 0.05° (~5km)
   - Update Frequency: Daily

2. **AfSIS Soil Data**

   - Source: Africa Soil Information Service
   - Format: GeoTIFF files
   - Resolution: 250m
   - Coverage: Sub-Saharan Africa

3. **FAOSTAT Yield Data**
   - Source: Food and Agriculture Organization
   - Format: CSV files
   - Update Frequency: Annual
   - Coverage: Global

### Data Processing Pipeline

```mermaid
graph TD
    A[Raw Data Sources] --> B[Data Ingestion]
    B --> C[Data Cleaning]
    C --> D[Feature Engineering]
    D --> E[Model Training]
    E --> F[Model Validation]
    F --> G[Model Deployment]
    G --> H[API Endpoints]
```

### Data Quality Assurance

- **Completeness**: Check for missing values and outliers
- **Consistency**: Validate data types and ranges
- **Accuracy**: Cross-reference with known benchmarks
- **Timeliness**: Ensure data freshness for predictions

---

## 🔒 Security Considerations

### API Security

1. **Rate Limiting**: Implement request throttling
2. **Input Validation**: Sanitize all user inputs
3. **CORS Configuration**: Restrict cross-origin requests
4. **Authentication**: JWT-based user authentication (future)

### Data Privacy

1. **PII Protection**: No personal information collected
2. **Data Encryption**: Encrypt sensitive data at rest
3. **Access Control**: Role-based access to admin functions
4. **Audit Logging**: Track all data access and modifications

---

## 📈 Performance Optimization

### Backend Optimization

1. **Caching**: Redis for frequently accessed data
2. **Database Indexing**: Optimize query performance
3. **Async Processing**: Non-blocking I/O operations
4. **Connection Pooling**: Efficient database connections

### Frontend Optimization

1. **Code Splitting**: Lazy load components
2. **Image Optimization**: Next.js automatic image optimization
3. **Bundle Analysis**: Monitor bundle size
4. **CDN Integration**: Distribute static assets globally

---

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

1. **Port Already in Use**

   ```bash
   # Check what's using port 8000
   netstat -ano | findstr :8000

   # Kill process
   taskkill /PID <PID> /F
   ```

2. **Model Loading Errors**

   ```bash
   # Check model file exists
   ls -la models/

   # Reinstall dependencies
   pip install -r requirements.txt
   ```

#### Frontend Issues

1. **Build Failures**

   ```bash
   # Clear cache
   rm -rf .next node_modules
   npm install
   npm run build
   ```

2. **API Connection Errors**

   ```bash
   # Check backend is running
   curl http://localhost:8000/health

   # Verify CORS settings
   ```

### Debug Mode

Enable debug logging:

```bash
# Backend
export DEBUG=True
export LOG_LEVEL=DEBUG

# Frontend
export NODE_ENV=development
```

---

## 🔄 Maintenance and Updates

### Regular Tasks

1. **Data Updates**: Monthly climate data refresh
2. **Model Retraining**: Quarterly model performance review
3. **Security Updates**: Monthly dependency updates
4. **Performance Monitoring**: Weekly system health checks

### Backup Strategy

1. **Database**: Daily automated backups
2. **Models**: Version control for trained models
3. **Configuration**: Environment-specific config files
4. **Logs**: Centralized log management

---

## 📞 Support and Contact

### Development Team

- **Lead Developer**: [Your Name]
- **ML Engineer**: [ML Engineer Name]
- **Frontend Developer**: [Frontend Developer Name]
- **DevOps Engineer**: [DevOps Engineer Name]

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Email**: dev@agri-adapt-ai.com
- **Slack**: #agri-adapt-ai channel
- **Documentation**: [Project Wiki](https://github.com/your-username/agri-adapt-ai/wiki)

---

## 📚 Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Polars Documentation](https://pola.rs/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

### Research Papers

- [Drought Impact on Maize Production in Kenya](link-to-paper)
- [Machine Learning in Agricultural Applications](link-to-paper)
- [Climate Data Integration for Crop Modeling](link-to-paper)

### Open Source Projects

- [CHIRPS Data Processing](https://github.com/chg-ucsb/chirps)
- [AfSIS Data Tools](https://github.com/afsis/afsis-tools)
- [Agricultural ML Models](https://github.com/agricultural-ml)

---

**Last Updated**: December 2024
**Version**: 1.2.0
**Maintainer**: [Your Name]
