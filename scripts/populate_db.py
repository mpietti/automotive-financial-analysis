import pandas as pd
import sqlite3
import os

db_path = os.path.join('data', 'portfolio.db')
raw_data_path = os.path.join('data', 'raw')

def populate_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    asset_info = {
        'RACE': ('Ferrari N.V.', 'Luxury Automotive'),
        'STLA': ('Stellantis N.V.', 'Automotive'),
        'TSLA': ('Tesla, Inc.', 'Electric Vehicles'),
        'GM': ('General Motors Company', 'Automotive')
    }

    print("starting data ingestion (prices & dividends)...")

    for ticker, info in asset_info.items():
        print(f"processing {ticker}...")
        
        # 1- insert or get asset id
        cursor.execute('INSERT OR IGNORE INTO assets (ticker, name, sector) VALUES (?, ?, ?)', (ticker, info[0], info[1]))
        cursor.execute('SELECT id FROM assets WHERE ticker = ?', (ticker,))
        asset_id = cursor.fetchone()[0]

        # 2- load and insert prices
        price_file = os.path.join(raw_data_path, f"{ticker}.csv")
        if os.path.exists(price_file):
            df_p = pd.read_csv(price_file)
            df_p.rename(columns={df_p.columns[0]: 'Date'}, inplace=True)
            df_p.columns = [c.title() for c in df_p.columns]
            
            for _, row in df_p.iterrows():
                cursor.execute('''
                    INSERT OR IGNORE INTO prices (asset_id, date, close_price, volume)
                    VALUES (?, ?, ?, ?)
                ''', (asset_id, row['Date'], row['Close'], row.get('Volume', 0)))

        # 3- load and insert dividends
        div_file = os.path.join(raw_data_path, f"{ticker}_dividends.csv")
        if os.path.exists(div_file):
            df_d = pd.read_csv(div_file)
            # yfinance dividends csv usually has 'Date' and 'Dividends' columns
            df_d.columns = [c.title() for c in df_d.columns]
            
            for _, row in df_d.iterrows():
                cursor.execute('''
                    INSERT OR IGNORE INTO dividends (asset_id, date, dividend_amount)
                    VALUES (?, ?, ?)
                ''', (asset_id, row['Date'], row['Dividends']))
            print(f" -> dividends loaded for {ticker}")

    conn.commit()
    conn.close()
    print("database population completed successfully.")

if __name__ == "__main__":
    populate_database()
