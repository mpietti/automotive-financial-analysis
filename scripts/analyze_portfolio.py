import pandas as pd
import numpy as np
import sqlite3
import os

# define database path
DB_PATH = os.path.join('data', 'portfolio.db')

def fetch_data_from_db():
    """
    Connects to the SQLite database and retrieves historical price data.
    Performs data cleaning to handle potential bad rows (e.g., headers in data).
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    
    # sql query: join prices with assets to get ticker symbols
    query = '''
    SELECT p.date, a.ticker, p.close_price
    FROM prices p
    JOIN assets a ON p.asset_id = a.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    
    # 1- convert 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # 2- convert 'close_price' to numeric
    df['close_price'] = pd.to_numeric(df['close_price'], errors='coerce')
    
    # 3- drop rows with invalid dates or prices (cleaning dirty data)
    df = df.dropna(subset=['date', 'close_price'])
    
    # 4- sort by date to ensure correct time-series analysis
    df = df.sort_values('date')
    
    # reshape dataframe: index = date, columns = tickers, values = close price
    df_pivot = df.pivot(index='date', columns='ticker', values='close_price')
    
    return df_pivot

def calculate_metrics(df):
    """
    Calculates key financial metrics: Cumulative Return, Volatility, Sharpe Ratio.
    """
    print("\n--- Financial Performance Report ---")
    print(f"Timeframe: {df.index.min().date()} to {df.index.max().date()}")
    
    # calculate daily returns %
    returns = df.pct_change().dropna()
    
    if returns.empty:
        print("Insufficient data to calculate returns.")
        return returns

    # 1- cumulative return
    cum_returns = (1 + returns).prod() - 1
    
    # 2- annualized volatility
    volatility = returns.std() * np.sqrt(252)
    
    # 3- sharpe ratio (return / risk),assuming risk-free rate = 0% for simplicity 
    sharpe_ratio = (returns.mean() * 252) / volatility
    
    # 4- compound annual growth rate)
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    cagr = (df.iloc[-1] / df.iloc[0]) ** (1/years) - 1

    # creating a summary dataframe
    summary = pd.DataFrame({
        'Cumulative Return': cum_returns,
        'CAGR': cagr,
        'Ann. Volatility': volatility,
        'Sharpe Ratio': sharpe_ratio
    })
    
    # display the report rounded to 4 decimal places
    print(summary.round(4))
    
    return returns

if __name__ == "__main__":
    try:
        print("Fetching data from database...")
        data = fetch_data_from_db()
        
        if not data.empty:
            calculate_metrics(data)
        else:
            print("No valid data found in the database.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
