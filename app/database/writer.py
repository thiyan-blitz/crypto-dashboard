from app.database.connection import get_sqlengine
from sqlalchemy import text

def write_crypto_data(records):
    engine=get_sqlengine()
    if not engine:
        print("No database engine exist")
        return False
    try:
        with engine.begin() as conn:

            insert_query=text("""
                INSERT INTO crypto_prices 
                (coin,price,market_cap,volume,price_change_24h,timestamp)
                VALUES (:coin, :price, :market_cap, :volume, :price_change_24h, :timestamp)""")
        
            conn.execute(insert_query, records)
        print(f"{len(records)} records inserted successfully.")
        return True
    except Exception as e:
        print(f"Failed to write data to database: {e}")
        return False

if __name__=="__main__":
    sample_records=[
        {
            "coin":"bitcoin",
            "price":105000,
            "market_cap":2000000000000,
            "volume":50000000000,
            "price_change_24h":2.5,
            "timestamp":"2024-06-01 12:00:00"
        }
    ]
    write_crypto_data(sample_records)