import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

INPUT_PATH = "data/processed/cleaned_headlines.txt"
OUTPUT_PATH = "data/processed/sentiment_output.txt"

# Load FinBERT
model_name = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Read cleaned headlines
with open(INPUT_PATH, "r") as f:
    headlines = f.readlines()

# Analyze sentiment
results = []
for headline in headlines:
    if headline.strip():
        result = classifier(headline.strip())[0]
        results.append((headline.strip(), result['label'], result['score']))

# Save results
os.makedirs("data/processed", exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    for text, label, score in results:
        f.write(f"{label.upper()} ({score:.2f}): {text}\n")

print(f"Sentiment results saved to {OUTPUT_PATH}")