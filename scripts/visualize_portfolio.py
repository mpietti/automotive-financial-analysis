import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os
import numpy as np

# configuration
DB_PATH = os.path.join('data', 'portfolio.db')
OUTPUT_DIR = 'models'

def generate_strategy_chart():
    # connect to the database
    conn = sqlite3.connect(DB_PATH)
    
    # query to fetch prices and tickers
    query = '''
        SELECT p.date, a.ticker, p.close_price 
        FROM prices p JOIN assets a ON p.asset_id = a.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    # timezone management
    df['date'] = pd.to_datetime(df['date'], utc=True, errors='coerce')
    df['date'] = df['date'].dt.tz_localize(None)
    df = df.dropna(subset=['date'])
    
    # pivot for time-series analysis
    prices_pivot = df.pivot(index='date', columns='ticker', values='close_price')
    
    # calculate daily returns
    returns = prices_pivot.pct_change()
    
    # equally weighted portfolio
    portfolio_returns = returns.mean(axis=1)
    
    # calculate cumulative returns (base 100)
    # individual assets performance
    individual_cum = (1 + returns).cumprod() * 100
    # portfolio performance
    portfolio_cum = (1 + portfolio_returns).cumprod() * 100

    # plotting
    plt.figure(figsize=(12, 6))
    
    for ticker in individual_cum.columns:
        plt.plot(individual_cum.index, individual_cum[ticker], label=ticker, alpha=0.5)
    
    plt.plot(portfolio_cum.index, portfolio_cum, label='PORTFOLIO PERFORMANCE', color='black', linewidth=3)

    plt.title('Portfolio Strategy Comparison vs Individual Stocks')
    plt.xlabel('Timeline')
    plt.ylabel('Investment Value ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # save the updated chart
    output_path = os.path.join(OUTPUT_DIR, 'portfolio_strategy_comparison.png')
    plt.savefig(output_path)
    print(f"Strategy chart updated successfully: {output_path}")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    generate_strategy_chart()
