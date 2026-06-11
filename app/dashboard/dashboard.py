import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
import plotly.express as px
import pandas as pd
from app.analytics.analyzer import(
    load_all_data,
    calculate_moving_average,
    calculate_volatility,
    calculate_correlation
)
from app.database.connection import get_sqlengine

st.set_page_config(
    page_title="Crypto Dashboard",
    layout="wide"
)

def load_data():
    engine=get_sqlengine()
    query="""
            SELECT coin,price,market_cap,volume,price_change_24h,timestamp
            FROM crypto_prices
            ORDER BY timestamp DESC
        """
    df=pd.read_sql(query,engine)
    return df

def get_latest(df):
    return df.groupby("coin").first().reset_index()

st.title("Crypto Monitoring Dashboard")
st.caption("Live data powered by CoinGecko API")

df=load_data()
latest=get_latest(df)

st.subheader("Live Prices")
cols=st.columns(4)
coins=["bitcoin","ethereum","solana","ripple"]
emojis=["₿", "Ξ", "◎", "✕"]

for i,(coin,emoji) in enumerate(zip(coins,emojis)):
    row=latest[latest["coin"]==coin]
    if not row.empty:
        price=row["price"].values[0]
        change=row["price_change_24h"].values[0]
        cols[i].metric(label=f"{emoji} {coin.capitalize()}",
                       value=f"${price:,.2f}",
                       delta=f"{change:.2f}%",
                       delta_color="normal"
                       )
st.divider()

st.subheader("Price Trends")

selected_coin=st.selectbox(
    "Select coin",
    ["bitcoin","ethereum","solana","ripple"],
    key="price_coin"
)

coin_df=df[df["coin"]==selected_coin].sort_values("timestamp")

fig=px.line(
            coin_df,
            x="timestamp",
            y="price",
            title=f"{selected_coin.capitalize()} Price Over Time",
            labels={"price":"Price(USD)","timestamp":"Time"},
            template="plotly_dark"
            )
fig.update_traces(line_color="#00ff88", line_width=2)
st.plotly_chart(fig)

vol_fig = px.bar(
    latest,
    x="coin",
    y="volume",
    title="Trading Volume by Coin",
    color="coin"
)
st.plotly_chart(vol_fig)

st.subheader("Analytics")

# ── Time Filter ──
time_filter = st.selectbox(
    "Select time range",
    ["Today", "This Week", "This Month"],
    key="time_filter"
)

analytics_df = load_all_data()

# Apply time filter
from datetime import datetime, timedelta
now = datetime.now()

if time_filter == "Today":
    cutoff = now - timedelta(days=1)
elif time_filter == "This Week":
    cutoff = now - timedelta(weeks=1)
elif time_filter == "This Month":
    cutoff = now - timedelta(days=30)

analytics_df["timestamp"] = pd.to_datetime(analytics_df["timestamp"])
analytics_df = analytics_df[analytics_df["timestamp"] >= cutoff]

analytics_coin = st.selectbox(
    "Select coin",
    ["bitcoin", "ethereum", "solana", "ripple"],
    key="coin_select"
)

# ── Volatility Chart ──
st.markdown("#### Volatility")
vol_df = calculate_volatility(analytics_df,analytics_coin)

fig_vol = px.line(
    vol_df,
    x="timestamp",
    y="volatility",
    title=f"{analytics_coin.capitalize()} — Rolling Volatility",
    labels={"volatility": "Volatility", "timestamp": "Time"},
    template="plotly_dark"
)
fig_vol.update_traces(line_color="#ff6b6b")
st.plotly_chart(fig_vol)

# ── Correlation Matrix ──
st.markdown("#### Correlation Matrix")
corr = calculate_correlation(analytics_df)

fig_corr = px.imshow(
    corr,
    title="Price Correlation Between Coins",
    template="plotly_dark",
    color_continuous_scale="RdYlGn",
    zmin=-1,
    zmax=1,
    text_auto=True
)
st.plotly_chart(fig_corr)

st.divider()

st.subheader("Latest Records")
st.dataframe(
    latest[["coin","price","market_cap","volume","price_change_24h","timestamp"]]
)

st.caption("Dashboard refreshes every 5 minutes")
