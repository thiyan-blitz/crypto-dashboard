import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY =os.getenv("COINGECKO_API_KEY")
BASE_URL = "https://api.coingecko.com/api/v3"

def fetch_crypto_data():
    try:
        url=f"{BASE_URL}/simple/price"
        params={
            "ids": "bitcoin,ethereum,solana,ripple",
            "vs_currencies": "usd",
            "include_market_cap":"true",
            "include_24hr_change":"true",
            "include_24hr_vol":"true",
            "x_cg_demo_api_key":API_KEY
        }

        response=requests.get(url,params=params)
        response.raise_for_status()
        data=response.json()
        print("Data fetched successfully!!")
        print(data)
        return data
    except Exception as e:
        print(f"Fetching failed:{e}")
        return None
if __name__=="__main__":
    fetch_crypto_data()
    
        