# i-sentiment-market-prediction

An AI-powered sentiment analysis system that extracts sentiment from financial news and social media to generate market predictions and alerts.

## Tech Stack

- Python (FinBERT, NLP, PyTorch)
- Golang (backend signal processing)
- PostgreSQL (storage)
- Telegram Bot (alerts)

## Structure

- `nlp/`: NLP pipeline and FinBERT training
- `backend/`: Golang microservice for execution logic
- `scripts/`: Data collectors and orchestrators
- `notebooks/`: Exploratory work and testing
- `reports/`: Backtesting results


/data
/notebooks
/src
  └── nlp/
  └── backend/
/models
/config
/docs
main.py
README.md
requirements.txt


structure

i-sentiment-market-prediction/
│
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 go.mod
├── 📄 .gitignore
│
├── 📁 data/                         # Raw & processed data
│   ├── raw/                        # Scraped or downloaded data (text, price)
│   └── processed/                  # Cleaned, structured datasets
│
├── 📁 notebooks/                   # Jupyter/Colab Notebooks
│   ├── 01_exploration.ipynb
│   ├── 02_finbert_inference.ipynb
│   └── 03_sentiment_price_merge.ipynb
│
├── 📁 nlp/                         # NLP pipeline (Python)
│   ├── __init__.py
│   ├── sentiment_model.py         # FinBERT model loading + inference
│   ├── preprocess.py              # Tokenization, cleaning, etc.
│   └── utils.py                   # Common helper functions
│
├── 📁 backend/                     # Backend (Golang)
│   ├── main.go                    # Main Golang app
│   ├── signal.go                  # Signal logic (thresholds, scoring)
│   ├── db.go                      # PostgreSQL connection + queries
│   └── telegram.go                # Telegram bot logic
│
├── 📁 config/                      # API keys, env configs
│   └── config.yaml
│
├── 📁 scripts/                     # Data fetching, preprocessing
│   ├── fetch_news.py              # News API
│   ├── fetch_prices.py            # Yahoo/Binance price history
│   └── sentiment_scoring.py       # End-to-end batch pipeline
│
├── 📁 tests/                       # Unit tests (Pytest, Go tests)
│
├── 📁 docker/                      # Docker setup
│   ├── Dockerfile.api
│   └── docker-compose.yml
│
└── 📁 reports/                     # Final figures, logs, and backtest results