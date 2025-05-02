# =============================================
# MAG7 Stock Dashboard Application
# Developed by Garrett Dudley
# Purpose: Analyze top 7 stocks (MAG7) using technical indicators (MA + RSI), calculate risk metrics, manage portfolios, and visualize charts.
# =============================================

# === Import necessary libraries ===
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import streamlit as st
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
from io import BytesIO

# === API Key and Stock List Setup ===
API_KEY = "IEM64CNUI8HTXV8P"
STOCKS = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'NVDA']

# Initialize Alpha Vantage API connection
ts = TimeSeries(key=API_KEY, output_format='pandas')

# Setup session state for persistent portfolio tracking
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# =============================================
# Function Definitions
# =============================================

# Fetch daily stock data from Alpha Vantage
def fetch_stock_data(symbol):
    try:
        data, _ = ts.get_daily(symbol=symbol, outputsize="full")
        data = data.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        data.index = pd.to_datetime(data.index)
        return data.sort_index()
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")
        return None

# Fetch latest real-time stock price
def fetch_latest_price(symbol):
    try:
        quote, _ = ts.get_quote_endpoint(symbol=symbol)
        price = float(quote['05. price'][0])
        return price
    except Exception as e:
        st.error(f"Error fetching latest price for {symbol}: {e}")
        return None

# Calculate RSI (Relative Strength Index)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Plot candlestick chart
def plot_candlestick(symbol, data):
    buf = BytesIO()
    mpf.plot(data, type='candle', volume=True, style='charles', title=f"{symbol} Candlestick Chart", savefig=dict(fname=buf, dpi=100, format='png'))
    buf.seek(0)
    return buf

# Plot moving averages and volume chart
def plot_moving_averages(symbol, data):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    ax[0].plot(data.index, data['Close'], label='Close', color='blue')
    ax[0].plot(data.index, data['MA20'], label='20-Day MA', linestyle='--', color='orange')
    ax[0].plot(data.index, data['MA50'], label='50-Day MA', linestyle='--', color='red')
    ax[0].legend()
    ax[1].bar(data.index, data['Volume'], color='gray', alpha=0.6)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

# Plot RSI chart
def plot_rsi_chart(data, rsi):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(rsi.index, rsi, label='RSI', color='purple')
    ax.axhline(70, color='red', linestyle='--')
    ax.axhline(30, color='green', linestyle='--')
    ax.fill_between(rsi.index, 70, rsi, where=(rsi>70), color='red', alpha=0.3)
    ax.fill_between(rsi.index, rsi, 30, where=(rsi<30), color='green', alpha=0.3)
    ax.set_title('Relative Strength Index (RSI)')
    ax.legend()
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

# Calculate risk metrics (returns, volatility, Sharpe ratio, max drawdown)
def calculate_risk_metrics(data):
    returns = data['Close'].pct_change().dropna()
    avg_daily_return = returns.mean()
    volatility_daily = returns.std()

    avg_annual_return = avg_daily_return * 252
    volatility_annual = volatility_daily * np.sqrt(252)

    sharpe_ratio_annualized = avg_annual_return / volatility_annual if volatility_annual != 0 else 0

    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    return avg_annual_return * 100, volatility_annual * 100, sharpe_ratio_annualized, max_drawdown * 100

# Generate trading signal based on Moving Averages and RSI combined
def generate_combined_signal(data):
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    rsi = calculate_rsi(data)

    if data['MA20'].iloc[-1] > data['MA50'].iloc[-1] and rsi.iloc[-1] < 70:
        return "BUY"
    elif data['MA20'].iloc[-1] < data['MA50'].iloc[-1] or rsi.iloc[-1] > 70:
        return "SELL"
    else:
        return "HOLD"

# Show and manage portfolio tracker manually
def show_portfolio():
    st.title("💼 Real-Time Portfolio Tracker")
    with st.form("portfolio_form"):
        symbol = st.text_input("Stock Symbol (e.g., AAPL)").upper()
        shares = st.number_input("Number of Shares", min_value=0.0, step=1.0)
        purchase = st.number_input("Purchase Price ($)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Stock")

    if submit and symbol and shares > 0 and purchase > 0:
        price = fetch_latest_price(symbol)
        if price:
            st.session_state.portfolio.append({
                'Symbol': symbol,
                'Shares': shares,
                'Purchase Price': purchase,
                'Current Price': price
            })

    if st.session_state.portfolio:
        df = pd.DataFrame(st.session_state.portfolio)
        df['Current Value'] = df['Shares'] * df['Current Price']
        df['Total Cost'] = df['Shares'] * df['Purchase Price']
        df['P/L ($)'] = df['Current Value'] - df['Total Cost']
        df['P/L (%)'] = (df['P/L ($)'] / df['Total Cost']) * 100

        st.dataframe(df.style.format({
            "Purchase Price": "${:.2f}",
            "Current Price": "${:.2f}",
            "Current Value": "${:.2f}",
            "Total Cost": "${:.2f}",
            "P/L ($)": "${:.2f}",
            "P/L (%)": "{:.2f}%"
        }))

        st.metric("Total Portfolio Value", f"${df['Current Value'].sum():,.2f}")
        st.metric("Total P/L", f"${df['P/L ($)'].sum():,.2f} ({df['P/L (%)'].mean():.2f}%)")

        st.subheader("📊 Portfolio Allocation")
        fig, ax = plt.subplots()
        ax.pie(df['Current Value'], labels=df['Symbol'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Portfolio as CSV", csv, "portfolio_report.csv", "text/csv")

# =============================================
# Streamlit App Main Logic
# =============================================

st.set_page_config(page_title="MAG7 Stock Dashboard", layout="wide")

# Sidebar mode selection
mode = st.sidebar.selectbox("Select Mode", ["Stock Analyzer", "Portfolio Tracker"])

# === Stock Analyzer Section ===
if mode == "Stock Analyzer":
    st.title("📈 MAG7 Stock Analyzer")
    symbol = st.sidebar.selectbox("Choose a Stock:", STOCKS)
    time_range = st.sidebar.selectbox("Select Time Range:", ["1 Month", "3 Months", "6 Months", "1 Year", "Max"])
    chart_type = st.sidebar.selectbox("Select Chart Type:", ["Both", "Candlestick", "Moving Averages"])

    if st.sidebar.button("Fetch Data"):
        data = fetch_stock_data(symbol)
        if data is not None:
            if time_range == "1 Month":
                data = data.last("30D")
            elif time_range == "3 Months":
                data = data.last("90D")
            elif time_range == "6 Months":
                data = data.last("180D")
            elif time_range == "1 Year":
                data = data.last("365D")

            signal = generate_combined_signal(data)
            if signal == "BUY":
                st.success("📈 Current Signal: BUY (Trend + RSI)")
            elif signal == "SELL":
                st.error("🔻 Current Signal: SELL (Trend or Overbought)")
            else:
                st.info("⚪ Current Signal: HOLD (Neutral)")

            avg_return, vol, sharpe, max_dd = calculate_risk_metrics(data)
            st.metric("Average Annual Return", f"{avg_return:.2f}%")
            st.metric("Annualized Volatility", f"{vol:.2f}%")
            st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            st.metric("Max Drawdown", f"{max_dd:.2f}%")

            if chart_type in ["Both", "Candlestick"]:
                st.subheader("Candlestick Chart")
                candle_img = plot_candlestick(symbol, data)
                st.image(candle_img, use_container_width=True)

            if chart_type in ["Both", "Moving Averages"]:
                st.subheader("Moving Averages and Volume")
                ma_img = plot_moving_averages(symbol, data)
                st.image(ma_img, use_container_width=True)

            st.subheader("Relative Strength Index (RSI)")
            rsi = calculate_rsi(data)
            rsi_img = plot_rsi_chart(data, rsi)
            st.image(rsi_img, use_container_width=True)

# === Portfolio Tracker Section ===
else:
    show_portfolio()

st.sidebar.caption("Developed with ❤️ using Streamlit")
