# src/price_fetcher.py

import yfinance as yf
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_price_data(ticker="AAPL", days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )

        if data.empty:
            logging.warning(f"No price data found for {ticker}.")
        else:
            logging.info(f"Fetched price data for {ticker}")
            logging.debug(f"\n{data[['Open', 'Close']].tail()}")

        return data
    except Exception as e:
        logging.error(f"Failed to fetch data for {ticker}: {str(e)}")
        return None

if __name__ == "__main__":
    fetch_price_data("AAPL")