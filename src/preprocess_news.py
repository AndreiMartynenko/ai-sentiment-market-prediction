import os
import re

INPUT_PATH = "data/raw/news_headlines.txt"
OUTPUT_PATH = "data/processed/cleaned_headlines.txt"

os.makedirs("data/processed", exist_ok=True)

def clean_text(text):
    text = text.strip()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # remove special characters
    return text.lower()

with open(INPUT_PATH, "r") as infile, open(OUTPUT_PATH, "w") as outfile:
    for line in infile:
        if line.strip() and not line.startswith("URL:"):
            cleaned = clean_text(line)
            outfile.write(cleaned + "\n")

print(f"Cleaned headlines saved to {OUTPUT_PATH}")