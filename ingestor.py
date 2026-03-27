import requests
import pandas as pd
from sqlalchemy import create_engine, text
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = "7WY7GYB3CX01UBZC" 
DB_URI = "postgresql://deepam@localhost:5432/saas_analytics"
SYMBOLS = ["CRM", "SNOW", "HUBS"]

def fetch_historical_market_data(symbol):
    print(f"📡 Fetching 12-month trend for {symbol}...")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Monthly Time Series" in data:
            series = data["Monthly Time Series"]
            history_list = []
            cutoff = datetime.now() - timedelta(days=365)
            
            for date_str, metrics in series.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                if date_obj >= cutoff:
                    history_list.append({
                        'ticker': symbol,
                        'price': float(metrics['4. close']),
                        'volume': int(metrics['5. volume']),
                        # REMOVED change_percent to fix the UndefinedColumn error
                        'last_trading_day': date_str,
                        'ingested_at': datetime.now()
                    })
            
            df = pd.DataFrame(history_list)
            engine = create_engine(DB_URI)

            # --- UPSERT LOGIC (Prevents Duplicates & Errors) ---
            # 1. Push to a temporary table
            df.to_sql('temp_market_sync', engine, if_exists='replace', index=False)
            
            # 2. Move from temp to main table using ON CONFLICT
            with engine.connect() as conn:
                upsert_query = text("""
                    INSERT INTO market_intelligence (ticker, price, volume, last_trading_day, ingested_at)
                    SELECT ticker, price, volume, CAST(last_trading_day AS DATE), ingested_at 
                    FROM temp_market_sync
                    ON CONFLICT (ticker, last_trading_day) 
                    DO UPDATE SET 
                        price = EXCLUDED.price,
                        volume = EXCLUDED.volume,
                        ingested_at = EXCLUDED.ingested_at;
                """)
                conn.execute(upsert_query)
                conn.commit()
                
            print(f"✅ 12 months of {symbol} data synced successfully.")
            
        else:
            print(f"⚠️ Error or Limit reached for {symbol}: {data}")
            
    except Exception as e:
        print(f"❌ Failed to ingest {symbol}: {e}")

if __name__ == "__main__":
    for s in SYMBOLS:
        fetch_historical_market_data(s)
        # 15 seconds is usually enough for 5 calls/min, but 20 is safer
        time.sleep(20)