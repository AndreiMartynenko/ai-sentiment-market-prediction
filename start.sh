#!/bin/bash

# Simple startup script - No Database, No Docker
# Just Python and ML models!

echo "🚀 Starting ProofOfSignal (Standalone Mode)"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Setup virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import uvicorn, streamlit, fastapi" 2>/dev/null || {
    echo "📥 Installing missing dependencies..."
    pip install -q uvicorn streamlit fastapi pydantic requests transformers torch pandas-ta solana
}

# Start ML Service
echo "🔬 Starting ML Service (Port 8000)..."
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/ml_service.log 2>&1 &
ML_PID=$!
sleep 3

# Check ML service
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ ML Service is running"
else
    echo "⚠️  ML Service starting... (check logs: tail -f /tmp/ml_service.log)"
fi

# Start Dashboard
echo "📊 Starting Homepage (Port 8501)..."
echo ""
echo "=========================================="
echo "✅ Services Started!"
echo "=========================================="
echo ""
echo "📍 Open in browser:"
echo "   🏠 http://localhost:8501"
echo ""
echo "📚 API Documentation:"
echo "   📖 http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Start Streamlit
streamlit run dashboard/homepage.py --server.port 8501

# Cleanup
trap "kill $ML_PID 2>/dev/null" EXIT

