# src/signal_generator.py

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

input_path = Path("data/processed/sentiment_output.txt")
output_path = Path("data/processed/trading_signals.txt")

# Check if sentiment file exists
if not input_path.exists():
    logging.error(f"Sentiment file not found: {input_path}")
    sys.exit(1)

# Read sentiment output
lines = input_path.read_text(encoding="utf-8").splitlines()
if not lines:
    logging.warning("Sentiment file is empty. No signals generated.")
    sys.exit(0)

# Generate signals
signals = []
for line in lines:
    if line.startswith("NEGATIVE"):
        signals.append(f"SHORT | {line}")
    elif line.startswith("POSITIVE"):
        signals.append(f"LONG | {line}")
    else:
        signals.append(f"NEUTRAL | {line}")

# Save signals
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8") as f:
    for signal in signals:
        f.write(signal + "\n")

logging.info(f"Signals saved to {output_path} ({len(signals)} entries)")