# Automotive Portfolio Analytics

A complete data engineering and financial analysis pipeline. 
This project extracts historical stock data (2023-2026), structures it into a relational database (SQLite), and performs advanced financial analytics on an automotive-focused portfolio featuring Ferrari, GM, Stellantis, Tesla.

This project represents my first professional step into the world of Data Engineering and Financial Analytics. As a beginner in SQL and Python, I built this end-to-end pipeline to challenge myself with real-world market data.
The goal was to move beyond simple spreadsheets and master the core technologies used by professional analysts: managing virtual environments, designing relational databases, and automating complex financial calculations.


---

## 1. Features
- **Automated Data Ingestion**: downloads historical prices and dividends directly from Yahoo Finance.
- **Advanced Risk Metrics**: calculates volatility, maximum drawdown, and total return.
- **Total Return Engine**: accounts for dividend reinvestment in performance charts.
- **Interactive Dashboard**: dynamic filtering and real-time metric updates.

## 2. Results
- **Performance**: Ferrari (RACE) shows the highest stability and growth during the 2023-2026 period.
- **Volatility**: Tesla (TSLA) maintains the highest volatility with a maximum drawdown exceeding 60%.
- **Dividend Impact**: inclusion of dividends significantly improves the total return for Stellantis (STLA) and GM compared to price-only returns.

## 3. Project Structure
- **data/**: contains the SQLite database (`portfolio.db`) and raw CSV files.
- **scripts/**:
  - `setup_db.py`: initializes the database schema.
  - `download_data.py`: fetches the latest market data.
  - `populate_db.py`: loads CSV data into the database.
  - `visualize_performance.py`: generates static PNG charts in `models/`.
  - `visualize_strategy.py`: generates strategic comparison charts.
- **models/**: stores static performance charts (Base 100).
- **app.py**: the main Streamlit web application.

## 4. Installation
1. Create a virtual environment:
   `python -m venv venv`
2. Activate it:
   `venv\Scripts\activate`
3. Install dependencies:
   `pip install -r requirements.txt`

## 5. Usage
1. **Update data**:
   `python scripts/download_data.py && python scripts/populate_db.py`
2. **Generate static charts**:
   `python scripts/visualize_performance.py`
3. **Launch web dashboard**:
   `streamlit run app.py`

## 6. Methodology
- **Total Return Calculation**: 
  $Total\ Return = \frac{Price_{t} + Dividend_{t}}{Price_{t-1}} - 1$
- **Data Range**: analysis covers data from early 2023 to February 2026.