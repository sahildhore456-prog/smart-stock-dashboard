import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64

# -------- Background Function --------
def set_bg(image_file):

    with open(image_file, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        }}

        h1, h2, h3 {{
        color: white;
        text-align: center;
        }}

        .stMetric {{
        background-color: rgba(0,0,0,0.6);
        padding: 10px;
        border-radius: 10px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# -------- Apply Background --------
set_bg("background.jpg")

# -------- Title --------
st.title("Smart Stock Market Analysis Dashboard")
st.write("NIFTY 50 Stock Analysis")

# -------- Get CSV Files --------
files = [f for f in os.listdir() if f.endswith(".csv")]

files = [f for f in files if "metadata" not in f.lower()]

# -------- Dropdown --------
stock = st.selectbox("Select Stock", files)

# -------- Load Data --------
data = pd.read_csv(stock)

data['Date'] = pd.to_datetime(data['Date'])

data['Close'] = pd.to_numeric(data['Close'])
data['Open'] = pd.to_numeric(data['Open'])
data['High'] = pd.to_numeric(data['High'])
data['Low'] = pd.to_numeric(data['Low'])

data = data.sort_values("Date")

latest = data.iloc[-1]

st.header(stock.replace(".csv",""))

# -------- Metrics --------
col1,col2,col3,col4 = st.columns(4)

col1.metric("Close", round(float(latest['Close']),2))
col2.metric("Open", round(float(latest['Open']),2))
col3.metric("High", round(float(latest['High']),2))
col4.metric("Low", round(float(latest['Low']),2))

# -------- Price Chart --------
st.subheader("Price Trend")

st.line_chart(data.set_index("Date")['Close'])

# -------- Candlestick --------
st.subheader("Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])

st.plotly_chart(fig)

# -------- Moving Average --------
data['MA20'] = data['Close'].rolling(20).mean()
data['MA50'] = data['Close'].rolling(50).mean()

st.subheader("Moving Average")

st.line_chart(data.set_index("Date")[['Close','MA20','MA50']])

# -------- RSI --------
delta = data['Close'].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

data['RSI'] = 100 - (100 /