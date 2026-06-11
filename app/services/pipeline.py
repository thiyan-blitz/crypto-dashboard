from app.services.fetcher import fetch_crypto_data
from app.services.transformer import transform_crypto_data
from app.database.writer import write_crypto_data
from app.services.alerts import run_alerts

def run_pipeline():
    raw_data=fetch_crypto_data()
    if not raw_data:
        return False

    records=transform_crypto_data(raw_data)
    if not records:
        return False
    
    success=write_crypto_data(records)

    if not success:
        return False
    run_alerts(records)
    print("Pipeline executed successfully!!")
    return True

if __name__=="__main__":
    run_pipeline()


