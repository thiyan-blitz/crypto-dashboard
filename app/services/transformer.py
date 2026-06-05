from datetime import datetime

def transform_crypto_data(raw_data):
    """
    Transforms raw cryptocurrency data into a structured format.

    Args:
        raw_data (dict): The raw data received from the cryptocurrency API.

    Returns:
        dict: A structured dictionary containing the transformed cryptocurrency data.
    """
    try:
        transformed=[]
        
        for c,v in raw_data.items():
            record={
                "coin":c,
                "price":v.get("usd",0),
                "volume":v.get("usd_24h_vol",0),
                "market_cap":v.get("usd_market_gap",0),
                "price_change_24h":v.get("usd_24h_change",0),
                "timestamp":datetime.now()
            }
            transformed.append(record)
            print(len(transformed))
        return transformed
    except Exception as e:
        print(f"Transformation failed:{e}")
        return []
    
if __name__=="__main__":
    sample = {
        "bitcoin": {
            "usd": 105000,
            "usd_market_cap": 2000000000000,
            "usd_24h_vol": 50000000000,
            "usd_24h_change": 2.5
        },
        "ethereum": {
            "usd": 4000,
            "usd_market_cap": 500000000000,
            "usd_24h_vol": 20000000000,
            "usd_24h_change": -1.2
        }
    }
    result=transform_crypto_data(sample)
    for record in result:
        print(record)
