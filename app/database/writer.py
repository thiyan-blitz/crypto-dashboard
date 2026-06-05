from app.database.connection import get_connection

def write_crypto_data(records):
    conn=get_connection()
    if not conn:
        print("No database connection exist")
        return False
    try:
        cursor=conn.cursor()

        insert_query="""
                INSERT INTO crypto_prices 
                (coin,price,market_cap,volume,price_change_24h,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s)"""
        
        for record in records:
            cursor.execute(insert_query,(
                record["coin"],
                record["price"],
                record["market_cap"],
                record["volume"],
                record["price_change_24h"],
                record["timestamp"]
            ))
        conn.commit()
        print(f"{len(records)} records inserted successfully.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Failed to write data to database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

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