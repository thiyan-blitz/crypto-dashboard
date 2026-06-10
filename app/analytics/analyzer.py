import pandas as pd
import numpy as np
from app.database.connection import get_connection

def load_all_data():
    conn=get_connection()
    query="""
            SELECT coin,price,volume,price_change_24h,timestamp
            FROM crypto_prices
            ORDER BY timestamp ASC"""
    df=pd.read_sql(query,conn)
    conn.close()
    return df

def calculate_moving_average(df,coin):
    coin_df=df[df["coin"]==coin].copy()
    coin_df=coin_df.sort_values("timestamp")
    coin_df["MA_7"]=coin_df.set_index("timestamp")["price"].rolling("7D").mean().values
    coin_df["MA_30"]=coin_df.set_index("timestamp")["price"].rolling("30D").mean().values
    return coin_df

def calculate_volatility(df,coin):
    coin_df=df[df["coin"]==coin].copy()
    coin_df=coin_df.sort_values("timestamp")
    coin_df["returns"]=coin_df["price"].pct_change()
    coin_df["volatility"]=coin_df["returns"].rolling(window=7).std()
    return coin_df

def calculate_correlation(df):
    pivot=df.pivot_table(
        index="timestamp",
        columns="coin",
        values="price"
    )
    correlation=pivot.corr()
    return correlation

if __name__=="__main__":
    df=load_all_data()
    
    print("Moving Averages - Bitcoin:")
    btc_ma = calculate_moving_average(df, "bitcoin")
    print(btc_ma[["timestamp", "price", "MA_7", "MA_30"]].tail(5))
    
    print("\nVolatility - Bitcoin:")
    btc_vol = calculate_volatility(df, "bitcoin")
    print(btc_vol[["timestamp", "price", "volatility"]].tail(5))
    
    print("\nCorrelation Matrix:")
    corr = calculate_correlation(df)
    print(corr)