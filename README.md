# AI Sentiment Market Prediction (Proof-of-Signal)

End-to-end demo app for generating crypto trading signals from:

- News sentiment (FinBERT-style)
- Technical indicators (EMA/RSI/MACD)

It also supports **proof-of-signal** via a deterministic SHA-256 hash (optional Solana devnet anchoring).


## Services / Ports

- Go API gateway: `http://localhost:8080`
- Python ML service (FastAPI): `http://localhost:8000`
- Next.js dashboard: `http://localhost:3000`

## Prerequisites

- Go (1.21+)
- Python (3.10+)
- Node.js (for the Next.js dashboard)

## Quick start (recommended: no DB)

1) Start ML service:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn ml_service.main:app --reload --port 8000
```

2) Start Go gateway:

```bash
NO_DB=true go run ./cmd/main.go
```

3) Start dashboard:

```bash
cd web3-app
npm install
npm run dev
```

Open `http://localhost:3000`.

## With database (optional)

By default, the demo runs without a database.

If you want DB-backed endpoints, start your own Postgres locally and set `DATABASE_URL`, then start Go without `NO_DB=true`.

## Test it (smoke tests)

### Go gateway

```bash
curl http://localhost:8080/health
curl "http://localhost:8080/api/v1/indicators?symbol=BTCUSDT"
```

### ML service

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","text":"Bitcoin reaches new all-time high"}'

curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT"}'
```

### Proof-of-signal (optional)

Enable Solana publishing in the ML service (devnet):

```bash
export SOLANA_PUBLISH_ENABLED=true
```

Then call `/hybrid` again and check `proof_hash` / `tx_signature` in the response.
