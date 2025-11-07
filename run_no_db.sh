#!/bin/bash

# Quick Start Script - No Database, No Docker
# Simple version that runs everything in memory

echo "🚀 Starting ProofOfSignal (No Database Mode)"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Check dependencies
echo "📦 Checking dependencies..."
python -c "import uvicorn, streamlit, requests" 2>/dev/null || {
    echo "Installing missing dependencies..."
    pip install -q uvicorn streamlit requests fastapi pydantic
}

# Start ML Service (no database)
echo "🔬 Starting ML Service (Port 8000) - No Database Mode..."
uvicorn ml_service.main_no_db:app --reload --host 0.0.0.0 --port 8000 > /tmp/ml_service_no_db.log 2>&1 &
ML_PID=$!
sleep 3

# Check if ML service started
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ ML Service is running"
else
    echo "⚠️  ML Service might not be ready yet..."
    echo "Check logs: tail -f /tmp/ml_service_no_db.log"
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
echo "📝 To generate a signal:"
echo "   1. Open http://localhost:8501"
echo "   2. Enter a symbol (e.g., BTCUSDT)"
echo "   3. Click 'Generate Signal'"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

# Start Streamlit
streamlit run dashboard/homepage_simple.py --server.port 8501

# Cleanup on exit
trap "kill $ML_PID 2>/dev/null" EXIT

