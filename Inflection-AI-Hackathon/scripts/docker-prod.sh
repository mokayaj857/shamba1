#!/bin/bash

# Production Docker Environment Script
echo "🚀 Starting Agri-Adapt AI Production Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if model file exists
if [ ! -f "models/maize_resilience_rf_model.joblib" ]; then
    echo "❌ Model file not found. Please ensure models/maize_resilience_rf_model.joblib exists."
    exit 1
fi

# Create necessary directories
mkdir -p data logs reports

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start production services
echo "🔨 Building production containers..."
docker-compose build

echo "🚀 Starting production services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Production environment is ready!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "🔧 To start with production database: docker-compose --profile production up -d"
echo ""
