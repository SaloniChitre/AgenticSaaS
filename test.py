import sqlalchemy
# Notice there is no password in the string below
engine = sqlalchemy.create_engine('postgresql://deepam@localhost:5432/saas_analytics')

try:
    with engine.connect() as conn:
        print("🚀 Connection Successful! DBeaver and Python are synced.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")