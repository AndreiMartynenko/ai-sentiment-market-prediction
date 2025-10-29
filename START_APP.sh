#!/bin/bash

echo "🚀 Starting AI Sentiment Market Prediction System"
echo "=================================================="

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Starting with Docker..."
    docker run -d --name sentiment_postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=sentiment_market \
        -p 5432:5432 \
        postgres:15-alpine
    echo "✅ PostgreSQL started"
    sleep 3
fi

# Start ML Service
echo "🔬 Starting ML Service (Port 8000)..."
cd /Users/developer/ai-sentiment-market-prediction
source venv/bin/activate
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000 &
ML_PID=$!

sleep 2

# Start Dashboard
echo "📊 Starting Dashboard (Port 8501)..."
streamlit run dashboard/app.py &
DASH_PID=$!

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📍 Access Points:"
echo "   🧠 ML Service: http://localhost:8000"
echo "   📊 Dashboard:  http://localhost:8501"
echo "   📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

wait
