#!/bin/bash

# AI Sentiment Market Prediction - System Startup Script
echo "🚀 Starting AI Sentiment Market Prediction System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys before running again."
    echo "   Required: NEWS_API_KEY, TWITTER_API_KEY, TELEGRAM_TOKEN"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs models data/raw data/processed

# Start the system with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Go API
if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo "✅ Go API is healthy"
else
    echo "❌ Go API is not responding"
fi

# Check ML Service
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ ML Service is healthy"
else
    echo "❌ ML Service is not responding"
fi

# Check Database
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database is not responding"
fi

echo ""
echo "🎉 System startup complete!"
echo ""
echo "📊 Service URLs:"
echo "   Go API: http://localhost:8080/api/v1/health"
echo "   ML Service: http://localhost:8000/health"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📚 API Documentation: docs/API_DOCUMENTATION.md"
echo "📖 Full Documentation: README.md"
echo ""
echo "🧪 Test the system:"
echo "   curl http://localhost:8080/api/v1/health"
echo "   curl -X POST http://localhost:8080/api/v1/sentiment/analyze -H 'Content-Type: application/json' -d '{\"text\": \"Apple stock is performing well\", \"model\": \"finbert\"}'"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop system: docker-compose down"
