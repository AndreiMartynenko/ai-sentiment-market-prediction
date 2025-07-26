# src/sentiment_analysis.py

import logging
import sys
from transformers import pipeline
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Paths
input_path = Path("data/raw/news_headlines.txt")
output_path = Path("data/processed/sentiment_output.txt")

# Load headlines
if not input_path.exists():
    logging.error(f"Input file not found: {input_path}")
    sys.exit(1)

headlines = input_path.read_text(encoding="utf-8").splitlines()
headlines = [h.strip() for h in headlines if h.strip()]

if not headlines:
    logging.warning("No headlines to analyze.")
    sys.exit(1)

# Load sentiment model
logging.info("🔍 Loading FinBERT sentiment model...")
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# Run sentiment analysis
logging.info(f"Analyzing {len(headlines)} headlines...")
results = classifier(headlines)

# Write output
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8") as f:
    for headline, result in zip(headlines, results):
        sentiment = result["label"]
        score = round(result["score"], 2)
        f.write(f"{sentiment} ({score}): {headline}\n")

logging.info(f"Sentiment results saved to {output_path}")