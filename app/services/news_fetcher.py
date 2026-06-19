import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY=os.getenv("NEWS_API_KEY")
BASE_URL="https://newsapi.org/v2/everything"

COIN_KEYWORDS={
    "bitcoin":"bitcoin BTC",
    "ethereum":"ethereum ETH",
    "solana":"solana SOL",
    "ripple":"ripple XRP"
}

def fetch_news(coin, page_size=10):
    try:
        params = {
            "q": COIN_KEYWORDS[coin],
            "language": "en",
            "pageSize": page_size,
            "apiKey": NEWS_API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        headlines = []
        for article in data.get("articles", []):
            title = article.get("title", "")
            if title and title != "[Removed]":
                headlines.append(title)

        print(f"Fetched {len(headlines)} headlines for {coin}")
        return headlines

    except Exception as e:
        print(f"News fetch failed for {coin}: {e}")
        return []
    
if __name__ == "__main__":
    for coin in ["bitcoin", "ethereum", "solana", "ripple"]:
        headlines = fetch_news(coin)  # ← headlines assigned here
        print(f"\n{coin.upper()} Headlines:")
        if headlines:
            for h in headlines:
                print(f"  → {h}")
        else:
            print("  No headlines fetched!")
        print()