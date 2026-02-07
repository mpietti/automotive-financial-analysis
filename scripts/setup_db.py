import sqlite3
import os

def create_database():
    db_path = os.path.join('data', 'portfolio.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        name TEXT,
        sector TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER,
        date TEXT NOT NULL,
        close_price REAL NOT NULL,
        volume INTEGER,
        FOREIGN KEY (asset_id) REFERENCES assets (id),
        UNIQUE(asset_id, date)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dividends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER,
        date TEXT NOT NULL,
        dividend_amount REAL NOT NULL,
        FOREIGN KEY (asset_id) REFERENCES assets (id),
        UNIQUE(asset_id, date)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"database schema verified/updated in: {db_path}")

if __name__ == "__main__":
    create_database()
