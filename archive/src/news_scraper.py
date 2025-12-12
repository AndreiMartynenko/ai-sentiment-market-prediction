#src/news_scraper.py

import logging
from dotenv import load_dotenv
import os
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    logging.error("Missing NEWS_API_KEY. Set it in your .env file.")
    raise ValueError("Missing NEWS_API_KEY. Set it in your .env file.")

# Define request parameters
url = "https://newsapi.org/v2/everything"
params = {
    "q": "stock market OR inflation OR earnings",
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 5,
    "apiKey": NEWS_API_KEY
}

logging.info("Sending request to NewsAPI...")
response = requests.get(url, params=params)

if response.status_code != 200:
    logging.error(f"API Error {response.status_code}: {response.text}")
    exit()

try:
    data = response.json()
except Exception as e:
    logging.exception("Failed to parse JSON response:")
    logging.debug("Raw response: %s", response.text)
    exit()

articles = data.get("articles", [])

if not articles:
    logging.warning("No articles found. Try adjusting the query.")
else:
    os.makedirs("data/raw", exist_ok=True)
    filepath = "data/raw/news_headlines.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        for i, article in enumerate(articles, 1):
            title = article["title"]
            description = article.get("description", "")
            url = article["url"]

            logging.info(f"{i}. {title}")
            f.write(f"{title} - {description}\n{url}\n\n")

    logging.info(f"✅ Headlines saved to {filepath}")