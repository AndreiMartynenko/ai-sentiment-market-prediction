#!/bin/bash

# Quick Start Script for ProofOfSignal Homepage
# This script starts the ML service and homepage dashboard locally

echo "🚀 Starting ProofOfSignal Application"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running."
    echo "Starting PostgreSQL with Docker..."
    docker run -d --name sentiment_postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=sentiment_market \
        -p 5432:5432 \
        postgres:15-alpine > /dev/null 2>&1
    
    echo "✅ PostgreSQL started"
    echo "⏳ Waiting for database to be ready..."
    sleep 5
    
    # Initialize database if needed
    if ! psql -h localhost -U postgres -d sentiment_market -c "SELECT 1" > /dev/null 2>&1; then
        echo "📊 Initializing database..."
        psql -h localhost -U postgres -d sentiment_market -f database/schema.sql > /dev/null 2>&1
        psql -h localhost -U postgres -d sentiment_market -f database/migration_add_tx_signature.sql > /dev/null 2>&1
        echo "✅ Database initialized"
    fi
fi

# Start ML Service in background
echo "🔬 Starting ML Service (Port 8000)..."
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/ml_service.log 2>&1 &
ML_PID=$!
sleep 3

# Check if ML service started
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  ML Service might not be ready yet. Continuing..."
else
    echo "✅ ML Service is running"
fi

# Start Dashboard
echo "📊 Starting Homepage Dashboard (Port 8501)..."
echo ""
echo "=========================================="
echo "✅ Services Started!"
echo "=========================================="
echo ""
echo "📍 Access Points:"
echo "   🏠 Homepage:     http://localhost:8501"
echo "   🔬 ML Service:   http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "📝 To generate signals:"
echo "   curl -X POST http://localhost:8000/hybrid \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"symbol\": \"BTCUSDT\"}'"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

# Start Streamlit
streamlit run dashboard/homepage.py --server.port 8501

# Cleanup on exit
trap "kill $ML_PID 2>/dev/null" EXIT

