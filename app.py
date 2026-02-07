import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
import plotly.express as px

# database configuration
DB_PATH = os.path.join('data', 'portfolio.db')

def load_full_data():
    conn = sqlite3.connect(DB_PATH)
    
    # 1- fetch daily prices
    df_prices = pd.read_sql_query('''
        SELECT p.date, a.ticker, p.close_price 
        FROM prices p JOIN assets a ON p.asset_id = a.id
    ''', conn)
    
    # 2- fetch dividends
    df_divs = pd.read_sql_query('''
        SELECT d.date, a.ticker, d.dividend_amount 
        FROM dividends d JOIN assets a ON d.asset_id = a.id
    ''', conn)
    conn.close()

    # data cleaning
    df_prices['date'] = pd.to_datetime(df_prices['date'], utc=True, errors='coerce').dt.tz_localize(None)
    df_divs['date'] = pd.to_datetime(df_divs['date'], utc=True, errors='coerce').dt.tz_localize(None)
    
    df_prices['close_price'] = pd.to_numeric(df_prices['close_price'], errors='coerce')
    df_divs['dividend_amount'] = pd.to_numeric(df_divs['dividend_amount'], errors='coerce')

    df_prices = df_prices.dropna(subset=['date', 'close_price'])
    df_divs = df_divs.dropna(subset=['date', 'dividend_amount'])

    prices_pivot = df_prices.pivot(index='date', columns='ticker', values='close_price')
    
    if not df_divs.empty:
        divs_pivot = df_divs.pivot(index='date', columns='ticker', values='dividend_amount')
        divs_pivot = divs_pivot.reindex(index=prices_pivot.index, columns=prices_pivot.columns).fillna(0)
    else:
        divs_pivot = pd.DataFrame(0.0, index=prices_pivot.index, columns=prices_pivot.columns)
    
    return prices_pivot, divs_pivot

# streamlit ui
st.set_page_config(page_title="Automotive Portfolio Analytics", layout="wide")
st.title("Automotive Portfolio Analytics Dashboard")

try:
    prices, dividends = load_full_data()
    
    if prices.empty:
        st.error("No valid price data found in database.")
    else:
        min_date = prices.index.min().strftime('%Y-%m-%d')
        max_date = prices.index.max().strftime('%Y-%m-%d')
        st.markdown(f"Interactive analysis tool. Data range: **{min_date}** to **{max_date}**")

        tickers = prices.columns.tolist()

        # sidebar
        st.sidebar.header("Portfolio Settings")
        selected_assets = st.sidebar.multiselect("Select assets", tickers, default=tickers)
        include_divs = st.sidebar.checkbox("Include Dividends (Total Return)", value=True)
        base_value = st.sidebar.number_input("Initial investment ($)", value=100.0)

        if selected_assets:
            p_filtered = prices[selected_assets]
            d_filtered = dividends[selected_assets]
            
            # calculations
            daily_price_change = p_filtered.pct_change().fillna(0)
            prev_prices = p_filtered.shift(1)
            dividend_yield = d_filtered / prev_prices
            dividend_yield = dividend_yield.fillna(0)
            
            if include_divs:
                daily_returns = daily_price_change + dividend_yield
                chart_title = "Cumulative Total Return (Growth + Dividends)"
            else:
                daily_returns = daily_price_change
                chart_title = "Cumulative Price Return (Capital Gains Only)"

            cum_growth = (1 + daily_returns).cumprod() * base_value

            # chart
            st.subheader(chart_title)
            fig = px.line(
                cum_growth, 
                labels={"value": "Investment Value ($)", "date": "Date"},
                template="plotly_white"
            )
            
            fig.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>"
            )

            fig.update_layout(
                yaxis_tickformat='$',
                hovermode="x unified",
                legend_title_text='Assets'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="main_performance_chart")

            # metrics table
            st.subheader(f"Performance Metrics (as of {max_date})")
            
            total_ret = ((cum_growth.iloc[-1] / base_value) - 1) * 100
            volatility = daily_returns.std() * np.sqrt(252) * 100
            rolling_max = cum_growth.cummax()
            drawdown = (cum_growth - rolling_max) / rolling_max
            max_dd = drawdown.min() * 100

            metrics_df = pd.DataFrame({
                "total return": total_ret,
                "ann. volatility": volatility,
                "max drawdown": max_dd
            })
            
            # formatting
            formatted_df = metrics_df.map(lambda x: f"{x:.2f}%")
            
            st.table(formatted_df)

        else:
            st.warning("Please select at least one asset from the sidebar.")

except Exception as e:
    st.error(f"Critical Error: {e}")
