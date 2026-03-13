# stock_project_comp.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64
import qrcode
from PIL import Image
import io

# ---------- Background Image ----------
def set_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as img:
            data = img.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
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

# Apply background (optional)
# set_bg("background.jpg")

# ---------- Title ----------
st.title("Smart Stock Market Analysis Dashboard")
st.write("NIFTY 50 Stock Analysis")

# ---------- Find CSV files automatically ----------
project_files = os.listdir()
data_files = [f for f in project_files if f.endswith(".csv")]
# Check if 'data' folder exists and add its CSVs too
if os.path.exists("data"):
    data_files += [os.path.join("data", f) for f in os.listdir("data") if f.endswith(".csv")]

# Remove duplicates
data_files = list(set(data_files))
# Remove metadata files
data_files = [f for f in data_files if "metadata" not in f.lower()]

if len(data_files) == 0:
    st.error("No CSV files found in the project folder or 'data' folder!")
    st.stop()

# ---------- Stock Selection ----------
stock_file = st.selectbox("Select Company", data_files)
stock_path = stock_file if os.path.exists(stock_file) else os.path.join("data", stock_file)

# ---------- Read Data ----------
try:
    data = pd.read_csv(stock_path)
except Exception as e:
    st.error(f"Error reading {stock_file}: {e}")
    st.stop()

# Convert data types
data['Date'] = pd.to_datetime(data['Date'])
for col in ['Open','High','Low','Close']:
    data[col] = pd.to_numeric(data[col], errors='coerce')
data = data.sort_values('Date')
latest = data.iloc[-1]

# ---------- Metrics ----------
st.header(os.path.basename(stock_file).replace(".csv",""))
col1, col2, col3, col4 = st.columns(4)
col1.metric("Close", round(float(latest['Close']),2))
col2.metric("Open", round(float(latest['Open']),2))
col3.metric("High", round(float(latest['High']),2))
col4.metric("Low", round(float(latest['Low']),2))

# ---------- Price Trend ----------
st.subheader("Price Trend")
st.line_chart(data.set_index("Date")['Close'])

# ---------- Candlestick Chart ----------
st.subheader("Candlestick Chart")
fig = go.Figure(data=[go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])
st.plotly_chart(fig)

# ---------- Moving Averages ----------
data['MA20'] = data['Close'].rolling(20).mean()
data['MA50'] = data['Close'].rolling(50).mean()
st.subheader("Moving Averages (20 & 50)")
st.line_chart(data.set_index("Date")[['Close','MA20','MA50']])

# ---------- RSI ----------
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

# ---------- MACD ----------
data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = data['EMA12'] - data['EMA26']
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
st.subheader("MACD")
st.line_chart(data.set_index("Date")[['MACD','Signal']])

# ---------- Trading Signal ----------
st.subheader("Trading Signal")
ma20 = data['MA20'].iloc[-1]
ma50 = data['MA50'].iloc[-1]

if ma20 > ma50 and latest_rsi < 70:
    st.success("BUY SIGNAL")
elif ma20 < ma50 and latest_rsi > 30:
    st.error("SELL SIGNAL")
else:
    st.warning("HOLD / WAIT")

# ---------- QR Code ----------
network_url = "http://192.168.1.103:8501"  # replace with your network URL
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=8,
    border=4,
)
qr.add_data(network_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)
st.subheader("Scan QR Code to Open Dashboard")
st.image(buf, caption="Scan to access the dashboard")