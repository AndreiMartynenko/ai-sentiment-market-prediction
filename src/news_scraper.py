from dotenv import load_dotenv
import os
import requests

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("Missing NEWS_API_KEY. Set it in your .env file.")

url = "https://newsapi.org/v2/everything"
params = {
    "q": "stock market OR inflation OR earnings",
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 5,
    "apiKey": NEWS_API_KEY
}

response = requests.get(url, params=params)

# Show response status code and content if there's an error
if response.status_code != 200:
    print(f"API Error {response.status_code}: {response.text}")
    exit()

try:
    data = response.json()
except Exception as e:
    print("Failed to parse JSON:", str(e))
    print("Raw response:", response.text)
    exit()

articles = data.get("articles", [])

if not articles:
    print("No articles found. Try adjusting the query.")
else:
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/news_headlines.txt", "w", encoding="utf-8") as f:
        for i, article in enumerate(articles, 1):
            title = article["title"]
            description = article.get("description", "")
            url = article["url"]

            print(f"{i}. {title}\n   {description}\n   URL: {url}\n---")
            f.write(f"{title} - {description}\n{url}\n\n")

    print("Headlines saved to data/raw/news_headlines.txt")