import requests
import os
from dotenv import load_dotenv
from app.database.connection import get_sqlengine
import pandas as pd

load_dotenv()

WEBHOOK_URL=os.getenv("DISCORD_WEBHOOK_URL")

ALERT_THRESHOLDS={
    "bitcoin":{"min":90000,"max":120000},
    "ethereum":{"min":2000,"max":4000},
    "solana":{"min":100,"max":300},
    "ripple":{"min":0.5,"max":3.0}
}

def send_discord_alert(message):
    try:
        payload={"content":message}
        response=requests.post(WEBHOOK_URL,json=payload)
        if response.status_code==204:
            print(f"Alert sent: {message}")
        else:
            print(f"Failed to send alert: {response.status_code}")
    except Exception as e:
        print(f"Discord error:{e}")

def check_price_alerts(data):
    for record in data:
        coin=record["coin"]
        price=record["price"]

        if coin not in ALERT_THRESHOLDS:
            continue

        thresholds=ALERT_THRESHOLDS[coin]

        if price<thresholds["min"]:
            send_discord_alert(
                f"**PRICE ALERT** | {coin.upper()}\n"
                f"Price dropped below $ threshold! \n"
                f"Current price: ${price:,.2f}\n"
                f"Threshold: ${thresholds['min']:,.2f}"
            )

        elif price > thresholds["max"]:
            send_discord_alert(
                f"**PRICE ALERT** | {coin.upper()}\n"
                f"Price exceeded threshold!\n"
                f"Current: ${price:,.2f}\n"
                f"Threshold: ${thresholds['max']:,.2f}"
            )
        
def check_volume_spike(data):
    engine=get_sqlengine()
    query="""
        SELECT coin,AVG(volume) as avg_volume
        FROM crypto_prices
        GROUP BY coin"""
            
    avg_df=pd.read_sql(query,engine)

    for record in data:
        coin=record["coin"]
        volume=record["volume"]
        avg_row=avg_df[avg_df["coin"]==coin]
        if avg_row.empty:
            continue

        avg_volume=avg_row["avg_volume"].values[0]
        if volume>avg_volume*2:
             send_discord_alert(
                f" **VOLUME SPIKE** | {coin.upper()}\n"
                f"Volume is 2x above average!\n"
                f"Current: ${volume:,.2f}\n"
                f"Average: ${avg_volume:,.2f}"
            )
             
def run_alerts(data):
    print("Running alert checks...")
    check_price_alerts(data)
    check_volume_spike(data)
    

if __name__=="__main__":
    sample=[
        {"coin": "bitcoin", "price": 85000, "volume": 50000000000},
        {"coin": "ethereum", "price": 6000, "volume": 20000000000},
    ]
    run_alerts(sample)

                
         