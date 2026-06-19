try:
    from textblob import TextBlob
except ImportError:
    print("Warning: textblob not installed. Install with: pip install textblob")
    TextBlob = None

from app.services.news_fetcher import fetch_news
from app.database.connection import get_sqlengine
from sqlalchemy import text
from datetime import datetime

def analyze_sentiment(headline):
    blob = TextBlob(headline)
    score = blob.sentiment.polarity

    if score > 0.1:
        label = "Positive"
    elif score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"

    return score, label

def store_sentiment(coin,headline,score,label):
    engine=get_sqlengine()

    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                        INSERT INTO sentiment
                              (coin,headline,sentiment_score,sentiment_label,timestamp)
                              VALUES (:coin,:headline,:score,:label,:timestamp)
                              """),
                              {
                                    "coin":coin,
                                    "headline": headline,
                                    "score": score,
                                    "label": label,
                                    "timestamp": datetime.now()
                              })
            conn.commit()
        return True
    except Exception as e:
        print(f"Failed to store sentiment:{e}")
        return False
def run_sentiment_analysis():
    coins = ["bitcoin", "ethereum", "solana", "ripple"]
    print("Running sentiment analysis...")

    for coin in coins:
        headlines = fetch_news(coin)
        if not headlines:
            print(f"No headlines for {coin}")
            continue

        for headline in headlines:
            score, label = analyze_sentiment(headline)
            store_sentiment(coin, headline, score, label)
            print(f"{coin.upper()} | {label} ({score:.4f}) | {headline[:50]}...")

    print("Sentiment analysis complete!")

if __name__ == "__main__":
    run_sentiment_analysis()
