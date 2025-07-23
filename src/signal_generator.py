import os

SENTIMENT_FILE = 'data/processed/sentiment_output.txt'
SIGNAL_FILE = 'data/processed/trading_signals.txt'

# Simple rule-based signal generation
def generate_signal(label, score):
    if label == 'POSITIVE' and score >= 0.95:
        return 'LONG'
    elif label == 'NEGATIVE' and score >= 0.95:
        return 'SHORT'
    else:
        return 'NEUTRAL'

# Main logic
def run_signal_generator():
    if not os.path.exists(SENTIMENT_FILE):
        print("Sentiment file not found. Please run sentiment_analysis.py first.")
        return

    signals = []
    with open(SENTIMENT_FILE, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                label_part, headline = line.strip().split(":", 1)
                label = label_part.split("(")[0].strip()
                score = float(label_part.split("(")[1].replace(")", ""))
                signal = generate_signal(label, score)
                signals.append(f"{signal} | {label} ({score:.2f}) | {headline.strip()}")
            except Exception as e:
                print(f"Error parsing line: {line}")
                continue

    os.makedirs(os.path.dirname(SIGNAL_FILE), exist_ok=True)
    with open(SIGNAL_FILE, 'w') as f:
        for signal_line in signals:
            f.write(signal_line + "\n")

    print(f"Signals saved to {SIGNAL_FILE}")

if __name__ == "__main__":
    run_signal_generator()