import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.title("Smart Stock Market Analysis Dashboard")
st.write("NIFTY 50 Stock Analysis")

# Folder path where CSV files are stored
data_folder = "data"

# Get all CSV files
files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

# Remove metadata file
files = [f for f in files if f != "stock_metadata.csv"]

# Stock selection
stock_file = st.selectbox("Select Stock", files)

# Load Data
file_path = os.path.join(data_folder, stock_file)

data = pd.read_csv(file_path)

# Convert columns
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
data['Open'] = pd.to_numeric(data['Open'], errors='coerce')
data['High'] = pd.to_numeric(data['High'], errors='coerce')
data['Low'] = pd.to_numeric(data['Low'], errors='coerce')

data = data.sort_values("Date")
data = data.dropna()

st.header(stock_file.replace(".csv",""))

latest = data.iloc[-1]

# Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Close", round(float(latest['Close']),2))
col2.metric("Open", round(float(latest['Open']),2))
col3.metric("High", round(float(latest['High']),2))
col4.metric("Low", round(float(latest['Low']),2))

# Price Trend
st.subheader("Price Trend")

st.line_chart(data.set_index("Date")['Close'])

# Candlestick Chart
st.subheader("Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])

st.plotly_chart(fig)

# Moving Average
data['MA20'] = data['Close'].rolling(20).mean()
data['MA50'] = data['Close'].rolling(50).mean()

st.subheader("Moving Average")

st.line_chart(data.set_index("Date")[['Close','MA20','MA50']])

# RSI
delta = data['Close'].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

data['RSI'] = 100 - (100 / (1 + rs))

st.subheader("RSI Indicator")

st.line_chart(data.set_index("Date")['RSI'])

latest_rsi = data['RSI'].iloc[-1]

st.write("Current RSI:", round(float(latest_rsi),2))

# MACD
data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()

data['MACD'] = data['EMA12'] - data['EMA26']
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

st.subheader("MACD")

st.line_chart(data.set_index("Date")[['MACD','Signal']])

# Trading Signal
st.subheader("Trading Signal")

ma20 = data['MA20'].iloc[-1]
ma50 = data['MA50'].iloc[-1]

if ma20 > ma50 and latest_rsi < 70:
    st.success("BUY SIGNAL")

elif ma20 < ma50 and latest_rsi > 30:
    st.error("SELL SIGNAL")

else:
    st.warning("HOLD / WAIT")