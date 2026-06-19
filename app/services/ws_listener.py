import json
import websocket
from sqlalchemy import text
from app.database.connection import get_sqlengine
import time

SYMBOLS=["btcusdt","ethusdt","solusdt","xrpusdt"]

STREAM_URL="wss://stream.binance.com:9443/stream?streams="+"/".join(f"{symbol}@trade" for symbol in SYMBOLS)

SYMBOL_TO_COIN = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple"
}

engine=get_sqlengine()

def upsert_live_price(coin,price):
    try:
        with engine.connect() as conn:
            conn.execute(text(""" 
                            INSERT INTO live_prices (coin,price,updated_at)
                             VALUES (:coin,:price,NOW())
                             ON CONFLICT (coin)
                             DO UPDATE SET price=:price,updated_at=NOW()
                                """),{"coin":coin,"price":price})
            conn.commit()
    except Exception as e:
        print(f"Failed to upsert {coin}:{e}")


last_print_time = {}
def on_message(ws,message):
    data=json.loads(message)
    payload=data.get("data",{})
    symbol=payload.get("s")
    price=payload.get("p")

    if symbol in SYMBOL_TO_COIN and price:
        coin=SYMBOL_TO_COIN[symbol]
        price=float(price)
        upsert_live_price(coin,price)
        now = time.time()
        if coin not in last_print_time or now - last_print_time[coin] >= 1:
            print(f"{coin.upper()}: ${price:,.4f}")
            last_print_time[coin] = now

def on_error(ws,error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed!")

def on_open(ws):
    print("WebSocket connected! Listening for live prices...")

if __name__=="__main__":
    ws=websocket.WebSocketApp(
        STREAM_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()
            