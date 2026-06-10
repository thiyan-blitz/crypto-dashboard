import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
import plotly.express as px
import pandas as pd

from app.database.connection import get_connection

st.set_page_config(
    page_title="Crypto Dashboard"
)

def load_data():
    conn=get_connection()
    query="""
            SELECT coin,price,market_cap,volume,price_change_24h,timestamp
            FROM crypto_prices
            ORDER BY timestamp DESC
        """
    df=pd.read_sql(query,conn)
    conn.close()
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
        delta_color="normal"
        cols[i].metric(label=f"{emoji} {coin.capitalize()}",
                       value=f"${price:,.2f}",
                       delta=f"{change:.2f}%"
                       )
st.divider()

st.subheader("Price Trends")

selected_coin=st.selectbox(
    "Select coin",
    ["bitcoin","ethereum","solana","ripple"]
)

coin_df=df[df["coin"]==selected_coin].sort_values("timestamp")

vol_fig=px.line(
            coin_df,
            x="timestamp",
            y="price",
            title=f"{selected_coin.capitalize()} Price Over Time",
            labels={"price":"Price(USD)","timestamp":"Time"},
            template="plotly_dark"
            )

st.plotly_chart(vol_fig,width="stretch")
st.divider()

st.subheader("Analytics")

from app.analytics.analyzer import(
    load_all_data,
    calculate_moving_average,
    calculate_volatility,
    calculate_correlation
)

analytics_coin=st.selectbox(
    "Select coin",
    ["bitcoin","ethereum","solana","ripple"],
    key="coin_select"
)

analytics_df=load_all_data()
st.markdown("#### Moving Averages")
ma_df=calculate_moving_average(analytics_df,analytics_coin)

ma_fig=px.line(
    ma_df,
    x="timestamp",
    y=["price","MA_7","MA_30"],
    title=f"{analytics_coin.capitalize()} Price & Moving Averages",
    labels={"value":"Price(USD)","timestamp":"Time"},
    template="plotly_dark"
)
st.plotly_chart(ma_fig)

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
    latest[["coin","price","market_cap","volume","price_change_24h","timestamp"]],
    width="stretch"
)

st.caption("Dashboard refreshes every 5 minutes")
