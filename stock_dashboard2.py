import streamlit as st
import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sahil@209",
    database="stock_app"
)

# Load data
query = "SELECT * FROM stocks"
data = pd.read_sql(query, conn)

data['date'] = pd.to_datetime(data['date'])

st.title("📈 Smart Stock Analysis Dashboard")

# Stock selector
symbols = data['symbol'].unique()
selected_stock = st.selectbox("Select Stock", symbols)

# Filter stock
stock_data = data[data['symbol'] == selected_stock]

# Indicators
stock_data['MA20'] = stock_data['close'].rolling(20).mean()
stock_data['Volatility'] = stock_data['close'].rolling(20).std()

# Charts
st.subheader("Stock Price")
st.line_chart(stock_data.set_index('date')['close'])

st.subheader("Price + Moving Average")
st.line_chart(stock_data.set_index('date')[['close','MA20']])

st.subheader("Volatility")
st.line_chart(stock_data.set_index('date')['Volatility'])