import psycopg2
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

def get_sqlengine():
    try:
        
        dbname=os.getenv("DB_NAME")
        user=os.getenv("DB_USER")
        password=os.getenv("DB_PASSWORD")
        host=os.getenv("DB_HOST")
        port=os.getenv("DB_PORT")
        
        engine=create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
        print("Database connected Successfully.")
        return engine
    except Exception as e:
        print("connection failed")
        return None

if __name__=="__main__":
    engine=get_sqlengine()
    if engine:
        print("Connection successful!")
    else:
        print("Connection failed!")

