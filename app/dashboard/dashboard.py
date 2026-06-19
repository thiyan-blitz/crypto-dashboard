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
from app.services.portfolio import get_portfolio_performance,add_holding
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

st.divider()

st.subheader("Portfolio Performance")
st.markdown("### Add Holding")
col1,col2,col3=st.columns(3)

with col1:
    p_coin=st.selectbox("Select coin",["bitcoin","ethereum","solana","ripple"],key="portfolio_coin")

with col2:
    p_quantity=st.number_input("Quantity",min_value=0.0,step=0.01,format="%.4f")
with col3:
    p_buyprice=st.number_input("Buy Price (USD)",min_value=0.0,step=0.01,format="%.2f")
if st.button("Add to Portfolio"):
    if p_quantity>0 and p_buyprice>0:
        success=add_holding(p_coin,p_quantity,p_buyprice)
        if success:
            st.success(f"Added {p_quantity} {p_coin} at ${p_buyprice}!")
        else:
            st.error("Failed to add holding!")

st.divider()
st.markdown("#### Portfolio Performance")
perf=get_portfolio_performance()

if perf.empty:
    st.info("No holdings yet-add some above!")
else:
    total_invested=perf["invested_value"].sum()
    total_current=perf["current_value"].sum()
    total_pnl=perf["profit_loss"].sum()
    total_pnl_pct=(total_current-total_invested)/total_invested*100

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Invested", f"${total_invested:,.2f}")
    k2.metric("Current Value", f"${total_current:,.2f}")
    k3.metric("Total P&L", f"${total_pnl:,.2f}", f"{total_pnl_pct:.2f}%")

    st.divider()
    st.markdown("#### Holdings Breakdown")

    st.dataframe(
        perf[[
            "coin","total_quantity","avg_buy_price",
            "current_value","profit_loss","profit_loss_pct"
        ]].rename(columns={
            "coin":"Coin",
            "total_quantity": "Quantity",
            "avg_buy_price": "Avg Buy Price",
            "current_value": "Current Value",
            "profit_loss": "P&L (USD)",
            "profit_loss_pct": "P&L (%)"
        })
    )

    st.markdown("#### Portfolio allocation")

    fig_pie=px.pie(
        perf,names="coin",
        values="current_value",
        title="Portfolio Allocation by Current Value",
        template="plotly_dark"
    )
    st.plotly_chart(fig_pie)

    st.divider()

    st.subheader("Sentiment Analysis")

    def load_sentiment_data():
        engine=get_sqlengine()
        query="""
            SELECT coin,headline,sentiment_score,sentiment_label,timestamp
            from sentiment
            ORDER BY timestamp DESC
            limit 40"""
        df=pd.read_sql(query,engine)
        return df
    
    sentiment_df=load_sentiment_data()

    if sentiment_df.empty:
        st.info("No sentiment data yet-run the sentiment analyzer first!")
    else:
        sentiment_coin=st.selectbox(
            "Select coin for sentiment",
            ["bitcoin","ethereum","solana","ripple"],
            key="sentiment_coin"
        )

        coin_sentiment=sentiment_df[sentiment_df["coin"]==sentiment_coin]

        avg_score=coin_sentiment["sentiment_score"].mean()
        positive_count=(coin_sentiment["sentiment_label"]=="Positive").sum()
        negative_count=(coin_sentiment["sentiment_label"]=="Negative").sum()
        neutral_count=(coin_sentiment["sentiment_label"]=="Neutral").sum()

        s1,s2,s3,s4=st.columns(4)
        s1.metric("AVg Sentiment Score",f"{avg_score:.3f}")
        s2.metric("Positive",positive_count)
        s3.metric("Neutral",neutral_count)
        s4.metric("negative",negative_count)

        sentiment_counts=coin_sentiment["sentiment_label"].value_counts().reset_index()
        sentiment_counts.columns=["label","count"]

        fig_sentiment_pie=px.pie(
            sentiment_counts,
            names="label",
        values="count",
        title=f"{sentiment_coin.capitalize()} Sentiment Distribution",
        color="label",
        color_discrete_map={
            "Positive": "#00ff88",
            "Negative": "#ff6b6b",
            "Neutral": "#888888"
        },
        template="plotly_dark"
        )
        st.plotly_chart(fig_sentiment_pie)

    # ── Latest Headlines Table ──
    st.markdown("#### Latest Headlines")
    st.dataframe(
            coin_sentiment[["headline", "sentiment_label"]]
            .rename(columns={"headline": "Headline", "sentiment_label": "Sentiment"})
    )
st.caption("Dashboard refreshes every 5 minutes")
