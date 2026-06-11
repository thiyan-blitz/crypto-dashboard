from app.database.connection import get_sqlengine
import pandas as pd
from sqlalchemy import text

def add_holding(coin,quantity,buy_price):
    engine=get_sqlengine()
    if not engine:
        print("No database engine exist")
        return False
    try:
        
        insert_query="""INSERT INTO portfolio (coin,quantity,buy_price)
            VALUES (:coin,:quantity,:buy_price)
        """
        with engine.begin() as conn:
            conn.execute(
                text(insert_query),
                {"coin":coin,"quantity":quantity,"buy_price":buy_price}
            )
        print(f"Holding added: {quantity} {coin} at ${buy_price}")
        return True
    except Exception as e:
        print(f"Failed to add holding: {e}")
        return False
    
def get_holdings():
    engine=get_sqlengine()
    query="""
        SELECT coin,
               sum(quantity) as total_quantity,
               AVG(buy_price) as avg_buy_price
        FROM portfolio
        GROUP BY coin
    """
    df=pd.read_sql(query,engine)
    return df

def get_portfolio_performance():
    engine=get_sqlengine()
    
    holdings=get_holdings()

    if holdings.empty:
        return pd.Dataframe()
    price_query="""
        SELECT DISTINCT ON (coin) coin,price
        FROM crypto_prices
        ORDER BY coin,timestamp DESC"""
    

    prices=pd.read_sql(price_query,engine)

    merged=holdings.merge(prices,on="coin",how="left")

    merged["invested_value"]=merged["total_quantity"]*merged["avg_buy_price"]
    merged["current_value"]=merged["total_quantity"]*merged["price"]
    merged["profit_loss"]=merged["current_value"]-merged["invested_value"]
    merged["profit_loss_pct"]=((merged["current_value"]-merged["invested_value"])/merged["invested_value"]*100
    )
    return merged

if __name__=="__main__":
    add_holding("bitcoin",0.5,95000)
    add_holding("ethereum",2.0,3500)
    add_holding("solana",10.0,180)

    print("\nPORTFOLIO PERFORMANCE:")
    perf=get_portfolio_performance()

    print(perf[["coin","total_quantity","avg_buy_price",
                "current_value","profit_loss","profit_loss_pct"]])
