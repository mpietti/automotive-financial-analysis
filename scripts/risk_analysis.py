import pandas as pd
import numpy as np
import sqlite3
import os

db_path = os.path.join('data', 'portfolio.db')

def fetch_data():
    conn = sqlite3.connect(db_path)
    df_prices = pd.read_sql_query('''
        SELECT p.date, a.ticker, p.close_price 
        FROM prices p JOIN assets a ON p.asset_id = a.id
    ''', conn)
    conn.close()

    # cleaning with timezone handling
    # 1- convert to datetime forcing utc to handle mixed offsets
    df_prices['date'] = pd.to_datetime(df_prices['date'], utc=True, errors='coerce')
    
    # 2- remove timezone information to avoid pivot/comparison errors
    df_prices['date'] = df_prices['date'].dt.tz_localize(None)
    
    df_prices = df_prices.dropna().sort_values('date')
    
    # pivot for time-series analysis
    prices_pivot = df_prices.pivot(index='date', columns='ticker', values='close_price')
    
    return prices_pivot

def calculate_risk_metrics(df):
    returns = df.pct_change().dropna()
    
    # 1- maximum drawdown
    roll_max = df.cummax()
    drawdowns = (df - roll_max) / roll_max
    max_drawdown = drawdowns.min()

    # 2- value at risk (var) - historical method at 95%
    var_95 = returns.quantile(0.05)

    # 3- summary table
    risk_summary = pd.DataFrame({
        'max drawdown': max_drawdown,
        'daily var (95%)': var_95,
        'ann. volatility': returns.std() * np.sqrt(252)
    })
    
    print("\n--- advanced risk metrics report ---")
    print(risk_summary.round(4))
    return drawdowns

if __name__ == "__main__":
    try:
        prices = fetch_data()
        if not prices.empty:
            calculate_risk_metrics(prices)
        else:
            print("no data found in database.")
    except Exception as e:
        print(f"error: {e}")
