import yfinance as yf
import os
import pandas as pd

assets = ['RACE', 'STLA', 'TSLA', 'GM']
start_date = "2023-01-01"
end_date = "2026-02-07"

def download_data():
    raw_path = os.path.join('data', 'raw')
    
    for ticker in assets:
        try:
            print(f"fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # download prices
            df_prices = stock.history(start=start_date, end=end_date)
            df_prices.to_csv(os.path.join(raw_path, f"{ticker}.csv"))
            
            # download dividends
            divs = stock.dividends
            if not divs.empty:
                divs.to_csv(os.path.join(raw_path, f"{ticker}_dividends.csv"))
                print(f"saved dividends for {ticker}")
            else:
                print(f"no dividends found for {ticker}")
                
        except Exception as e:
            print(f"error downloading {ticker}: {e}")

if __name__ == "__main__":
    download_data()
