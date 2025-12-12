# src/preprocess_news.py

import os
import re
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

INPUT_PATH = "data/raw/news_headlines.txt"
OUTPUT_PATH = "data/processed/cleaned_headlines.txt"

# Ensure output directory exists
os.makedirs("data/processed", exist_ok=True)

def clean_text(text):
    text = text.strip()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # remove special characters
    return text.lower()

try:
    with open(INPUT_PATH, "r", encoding="utf-8") as infile, open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
        for line in infile:
            if line.strip() and not line.startswith("URL:"):
                cleaned = clean_text(line)
                outfile.write(cleaned + "\n")
    logging.info(f"Cleaned headlines saved to {OUTPUT_PATH}")
except FileNotFoundError:
    logging.error(f"Input file not found at {INPUT_PATH}")
except Exception as e:
    logging.exception("An error occurred while processing headlines.")