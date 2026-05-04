import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

N = 52000

STAGES = [
    "Prospecting", "Qualification", "Needs Analysis",
    "Value Proposition", "Decision Makers", "Proposal/Price Quote",
    "Negotiation/Review", "Closed Won", "Closed Lost"
]
STAGE_WEIGHTS = [0.18, 0.14, 0.13, 0.11, 0.09, 0.12, 0.08, 0.08, 0.07]

INDUSTRIES = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
              "Real Estate", "Education", "Energy", "Logistics", "Media"]
REGIONS    = ["North America", "EMEA", "APAC", "LATAM"]
PRODUCTS   = ["Enterprise Suite", "Pro Plan", "Starter Pack",
              "Add-On Services", "Professional Services", "Support Bundle"]
REPS       = [f"Rep_{i:03d}" for i in range(1, 51)]
MANAGERS   = [f"Manager_{i:02d}" for i in range(1, 8)]

REP_TIER = {rep: ("Top" if i < 10 else "Mid" if i < 30 else "Low")
            for i, rep in enumerate(REPS)}
REP_MANAGER = {rep: MANAGERS[i % len(MANAGERS)] for i, rep in enumerate(REPS)}

start_date = datetime(2022, 1, 1)
end_date   = datetime(2024, 12, 31)

records = []
for opp_id in range(1, N + 1):
    rep      = random.choice(REPS)
    tier     = REP_TIER[rep]
    stage    = random.choices(STAGES, weights=STAGE_WEIGHTS, k=1)[0]
    product  = random.choice(PRODUCTS)
    created  = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    base_ttc  = {"Prospecting":120,"Qualification":90,"Needs Analysis":75,
                 "Value Proposition":60,"Decision Makers":55,
                 "Proposal/Price Quote":45,"Negotiation/Review":30,
                 "Closed Won":20,"Closed Lost":25}
    tier_mult = {"Top":0.75,"Mid":1.0,"Low":1.35}
    ttc       = int(base_ttc[stage] * tier_mult[tier] * np.random.uniform(0.7, 1.4))

    base_val  = {"Enterprise Suite":85000,"Pro Plan":32000,"Starter Pack":8500,
                 "Add-On Services":14000,"Professional Services":55000,"Support Bundle":9500}
    value     = base_val[product] * np.random.uniform(0.6, 2.2)

    forecast_rate = {"Top":0.72,"Mid":0.52,"Low":0.38}[tier] * np.random.uniform(0.9, 1.1)
    actual_rate   = forecast_rate * np.random.uniform(0.65, 1.15)

    last_activity = created + timedelta(days=random.randint(1, max(ttc, 1)))
    close_date    = created + timedelta(days=ttc)

    records.append({
        "opportunity_id":      f"OPP-{opp_id:06d}",
        "account_name":        f"Account_{random.randint(1,8000):05d}",
        "rep_name":            rep,
        "manager":             REP_MANAGER[rep],
        "rep_tier":            tier,
        "stage":               stage,
        "industry":            random.choice(INDUSTRIES),
        "region":              random.choice(REGIONS),
        "product":             product,
        "deal_value":          round(value, 2),
        "created_date":        created.strftime("%Y-%m-%d"),
        "close_date":          min(close_date, end_date).strftime("%Y-%m-%d"),
        "time_to_close_days":  ttc,
        "last_activity_date":  last_activity.strftime("%Y-%m-%d"),
        "calls_made":          random.randint(1, 20),
        "emails_sent":         random.randint(2, 35),
        "meetings_held":       random.randint(0, 8),
        "forecast_close_rate": round(forecast_rate, 4),
        "actual_close_rate":   round(actual_rate, 4),
        "fiscal_year":         created.year,
        "fiscal_quarter":      (created.month - 1) // 3 + 1,
    })

df = pd.DataFrame(records)
df.to_csv("crm_raw.csv", index=False)
print(f"✅ Generated {len(df):,} records")