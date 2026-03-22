import streamlit as st
import requests
import pandas as pd

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

st.title("📊 Cryptocurrency Dashboard")
st.write("Live data powered by CoinGecko API")

# -------------------------------
# Cached API Function
# -------------------------------
@st.cache_data(ttl=300)
def fetch_market_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    return response.json()


@st.cache_data(ttl=300)
def fetch_price_history(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    return response.json()

# -------------------------------
# Load Market Data
# -------------------------------
data = fetch_market_data()

if data is None:
    st.error("❌ Failed to load market data. Please try again later.")
    st.stop()

df = pd.DataFrame(data)

# -------------------------------
# Sidebar Inputs (2+ widgets ✅)
# -------------------------------
st.sidebar.header("User Controls")

coin_list = df["id"].tolist()
selected_coin = st.sidebar.selectbox("Select Cryptocurrency", coin_list)

days = st.sidebar.slider("Select Time Range (Days)", 1, 30, 7)

top_n = st.sidebar.slider("Top Coins for Bar Chart", 5, 20, 10)

# -------------------------------
# Filter Selected Coin
# -------------------------------
coin_data = df[df["id"] == selected_coin].iloc[0]

# -------------------------------
# KPI Metrics ✅
# -------------------------------
st.subheader(f"📌 {selected_coin.capitalize()} Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Current Price (USD)", f"${coin_data['current_price']:.2f}")
col2.metric("Market Cap", f"${coin_data['market_cap']:,}")
col3.metric("24h Change (%)", f"{coin_data['price_change_percentage_24h']:.2f}%")

# -------------------------------
# Fetch Time Series Data
# -------------------------------
history = fetch_price_history(selected_coin, days)

if history is None:
    st.error("❌ Failed to load historical data.")
    st.stop()

price_data = history["prices"]

# Convert to DataFrame
price_df = pd.DataFrame(price_data, columns=["timestamp", "price"])
price_df["timestamp"] = pd.to_datetime(price_df["timestamp"], unit="ms")
price_df = price_df.set_index("timestamp")

# -------------------------------
# Time Series Chart (REQUIRED ✅)
# -------------------------------
st.subheader("📈 Price Over Time")

st.line_chart(price_df["price"])

# -------------------------------
# Bar Chart ✅
# -------------------------------
st.subheader(f"📊 Top {top_n} Cryptocurrencies by Market Cap")

top_df = df.sort_values(by="market_cap", ascending=False).head(top_n)
bar_df = top_df.set_index("name")

st.bar_chart(bar_df["market_cap"])

# -------------------------------
# Data Table ✅
# -------------------------------
st.subheader("📋 Market Data Table")

display_df = df[[
    "name",
    "current_price",
    "market_cap",
    "total_volume",
    "price_change_percentage_24h"
]]

st.dataframe(display_df)

# -------------------------------
# Footer
# -------------------------------
st.write("---")
st.write("Dashboard built with Streamlit • Data from CoinGecko")