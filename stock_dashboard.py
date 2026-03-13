import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

st.title("📈 NIFTY 50 Stock Analysis Dashboard")

# Nifty 50 company list
nifty50 = {
"Reliance Industries":"RELIANCE.NS",
"TCS":"TCS.NS",
"Infosys":"INFY.NS",
"HDFC Bank":"HDFCBANK.NS",
"ICICI Bank":"ICICIBANK.NS",
"Hindustan Unilever":"HINDUNILVR.NS",
"ITC":"ITC.NS",
"SBI":"SBIN.NS",
"Bharti Airtel":"BHARTIARTL.NS",
"Larsen & Toubro":"LT.NS",
"Axis Bank":"AXISBANK.NS",
"Kotak Bank":"KOTAKBANK.NS",
"Asian Paints":"ASIANPAINT.NS",
"Maruti Suzuki":"MARUTI.NS",
"Sun Pharma":"SUNPHARMA.NS"
}

# User selects company
company = st.selectbox("Select Company", list(nifty50.keys()))

ticker = nifty50[company]

# Download data
data = yf.download(ticker, period="6mo", interval="1d")

# Candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])

fig.update_layout(title=company + " Candlestick Chart")

st.plotly_chart(fig)

# RSI
rsi = RSIIndicator(close=data['Close'].squeeze()).rsi()
data['RSI'] = rsi

st.subheader("RSI Indicator")

st.line_chart(data['RSI'])

# MACD
macd = MACD(close=data['Close'].squeeze())

data['MACD'] = macd.macd()
data['Signal'] = macd.macd_signal()

st.subheader("MACD Indicator")

st.line_chart(data[['MACD','Signal']])

st.write("Latest Price:", data['Close'].iloc[-1])