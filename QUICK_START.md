# ⚡ Quick Start - ProofOfSignal

## 🐳 Option 1: Docker (Easiest - 3 commands)

```bash
cd /Users/developer/ai-sentiment-market-prediction

# Start everything
docker-compose up -d

# View logs (optional)
docker-compose logs -f

# Open in browser
open http://localhost:8501
```

**Done!** 🎉 The homepage is now running at http://localhost:8501

---

## 💻 Option 2: Local Development (2 terminals)

### Terminal 1: ML Service
```bash
cd /Users/developer/ai-sentiment-market-prediction
source venv/bin/activate
uvicorn ml_service.main:app --reload --port 8000
```

### Terminal 2: Homepage
```bash
cd /Users/developer/ai-sentiment-market-prediction
source venv/bin/activate
streamlit run dashboard/homepage.py --server.port 8501
```

**Done!** 🎉 Open http://localhost:8501

---

## 🚀 Option 3: One-Command Script

```bash
cd /Users/developer/ai-sentiment-market-prediction
./start_homepage.sh
```

**Done!** 🎉 Open http://localhost:8501

---

## 🧪 Generate Your First Signal

```bash
curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

Then refresh the homepage to see it! 🔄

---

## 📍 URLs

- **Homepage**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ❌ Stop Services

**Docker:**
```bash
docker-compose down
```

**Local:**
- Press `Ctrl+C` in each terminal

---

For detailed instructions, see [HOW_TO_RUN.md](./HOW_TO_RUN.md)
