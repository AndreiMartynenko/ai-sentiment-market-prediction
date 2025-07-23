# src/price_fetcher.py
import yfinance as yf
from datetime import datetime, timedelta

def fetch_price_data(ticker="AAPL", days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    if data.empty:
        print("No price data found.")
    else:
        print(f"Fetched price data for {ticker}")
        print(data[['Open', 'Close']].tail())

    return data

if __name__ == "__main__":
    fetch_price_data("AAPL")