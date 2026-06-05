import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        conn=psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Database connected Successfully.")
        return conn
    except Exception as e:
        print("connection failed")
        return None

if __name__=="__main__":
    conn=get_connection()
    if conn:
        conn.close()
        print("Connection closed.")

