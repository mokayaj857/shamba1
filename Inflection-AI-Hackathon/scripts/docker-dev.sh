#!/bin/bash

# Development Docker Environment Script
echo "🚀 Starting Agri-Adapt AI Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if model file exists
if [ ! -f "models/maize_resilience_rf_model.joblib" ]; then
    echo "⚠️  Model file not found. Creating placeholder..."
    mkdir -p models
    echo "Placeholder model file - replace with actual trained model" > models/maize_resilience_rf_model.joblib
fi

# Create necessary directories
mkdir -p data logs reports

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down

# Build and start development services
echo "🔨 Building development containers..."
docker-compose -f docker-compose.dev.yml build

echo "🚀 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.dev.yml down"
echo ""
