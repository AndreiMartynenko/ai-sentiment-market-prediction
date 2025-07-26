def classify_action(sentiment_label):
    if "NEGATIVE" in sentiment_label:
        return "SHORT"
    elif "POSITIVE" in sentiment_label:
        return "LONG"
    return "NEUTRAL"

def parse_sentiment_line(line):
    parts = line.split(": ", 1)
    if len(parts) == 2:
        sentiment = parts[0].strip()
        headline = parts[1].strip()
        return sentiment, headline
    return "", line.strip()