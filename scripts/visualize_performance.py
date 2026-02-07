import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# configuration
DB_PATH = os.path.join('data', 'portfolio.db')
OUTPUT_DIR = 'models'

def generate_updated_charts():
    # connect to the database
    conn = sqlite3.connect(DB_PATH)
    
    # query to fetch prices and tickers
    query = '''
        SELECT p.date, a.ticker, p.close_price 
        FROM prices p JOIN assets a ON p.asset_id = a.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

       # force utc to manage different offsets
    df['date'] = pd.to_datetime(df['date'], utc=True, errors='coerce')
    df['date'] = df['date'].dt.tz_localize(None)
    df = df.dropna(subset=['date'])
    
    # pivot the data for time-series analysis
    prices_pivot = df.pivot(index='date', columns='ticker', values='close_price')
    
    # calculate cumulative returns starting from 100
    # formula: (current price / initial price) * 100
    normalized_prices = (prices_pivot / prices_pivot.iloc[0]) * 100

    # portfolio performance chart
    plt.figure(figsize=(12, 6))
    for ticker in normalized_prices.columns:
        plt.plot(normalized_prices.index, normalized_prices[ticker], label=ticker)

    plt.title('Automotive Stocks Performance (Base 100$)')
    plt.xlabel('Timeline')
    plt.ylabel('Investment Value ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # save the chart to models folder
    output_path = os.path.join(OUTPUT_DIR, 'portfolio_chart_100.png')
    plt.savefig(output_path)
    print(f"Chart updated successfully: {output_path}")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    generate_updated_charts()
