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

st.subheader("Latest Records")
st.dataframe(
    latest[["coin","price","market_cap","volume","price_change_24h","timestamp"]],
    width="stretch"
)

st.caption("Dashboard refreshes every 5 minutes")
