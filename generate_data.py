import pandas as pd
from sqlalchemy import create_engine
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to your new database
engine = create_engine('postgresql://deepam@localhost:5432/saas_analytics')
fake = Faker()

# 1. Create 500 Users
users = [{'user_id': i, 'email': fake.email(), 'signup_date': fake.date_between(start_date='-2y', end_date='today')} for i in range(1, 501)]
df_users = pd.DataFrame(users)

# 2. Create Plans
plans = [{'plan_id': 1, 'name': 'Basic', 'price': 10}, {'plan_id': 2, 'name': 'Pro', 'price': 30}]
df_plans = pd.DataFrame(plans)

# 3. Generate Subscription Payments (The logic engine)
subs = []
for _, user in df_users.iterrows():
    curr_date = user['signup_date']
    plan = random.choice(plans)
    # Randomly simulate 1 to 24 months of activity
    for _ in range(random.randint(1, 24)):
        if curr_date > datetime.now().date(): break
        subs.append({'user_id': user['user_id'], 'plan_id': plan['plan_id'], 'amount': plan['price'], 'payment_date': curr_date})
        curr_date += timedelta(days=31) # Monthly billing

# Push to Postgres
df_users.to_sql('users', engine, if_exists='replace', index=False)
df_plans.to_sql('plans', engine, if_exists='replace', index=False)
pd.DataFrame(subs).to_sql('subscriptions', engine, if_exists='replace', index=False)

print("✅ Data successfully generated in 'saas_analytics'!")