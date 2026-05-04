"""
ETL PIPELINE — CRM Sales Pipeline
Extract → Transform → Load
"""

import pandas as pd
import numpy as np
import sqlite3

# ── EXTRACT ──────────────────────────────────────────────────
df = pd.read_csv("crm_raw.csv", parse_dates=["created_date", "close_date", "last_activity_date"])
print(f"Extracted: {len(df):,} rows")

# ── TRANSFORM ─────────────────────────────────────────────────

# 1. Standardize stage names (real-world data is always messy)
STAGE_MAP = {
    "Prospecting": "Prospecting", "Qualification": "Qualification",
    "Needs Analysis": "Needs Analysis", "Value Proposition": "Value Proposition",
    "Decision Makers": "Decision Makers", "Proposal/Price Quote": "Proposal/Price Quote",
    "Negotiation/Review": "Negotiation/Review",
    "Closed Won": "Closed Won", "closed won": "Closed Won",
    "CLOSED WON": "Closed Won", "Won": "Closed Won",
    "Closed Lost": "Closed Lost", "closed lost": "Closed Lost",
    "CLOSED LOST": "Closed Lost", "Lost": "Closed Lost",
}
df["stage"] = df["stage"].map(STAGE_MAP)

# 2. Fill nulls
df["industry"]           = df["industry"].fillna("Unknown")
df["last_activity_date"] = df["last_activity_date"].fillna(df["created_date"])

# 3. Feature engineering — this is what makes your analysis possible
df["weighted_value"]       = df["deal_value"] * df["stage"].map({
    "Prospecting": 0.10, "Qualification": 0.20, "Needs Analysis": 0.30,
    "Value Proposition": 0.40, "Decision Makers": 0.50,
    "Proposal/Price Quote": 0.65, "Negotiation/Review": 0.80,
    "Closed Won": 1.00, "Closed Lost": 0.00
})
df["activity_score"]       = df["calls_made"] * 1.0 + df["emails_sent"] * 0.5 + df["meetings_held"] * 3.0
df["forecast_gap_pct"]     = ((df["forecast_close_rate"] - df["actual_close_rate"]) / df["forecast_close_rate"] * 100).round(2)
df["rep_utilization_rate"] = (df["activity_score"] / df["time_to_close_days"].replace(0, 1)).round(4)
df["is_won"]               = (df["stage"] == "Closed Won").astype(int)
df["is_lost"]              = (df["stage"] == "Closed Lost").astype(int)

CLOSED_STAGES = ["Closed Won", "Closed Lost"]
OPEN_STAGES   = [s for s in STAGE_MAP.values() if s not in CLOSED_STAGES]
df["is_stale"]     = ((df["stage"].isin(OPEN_STAGES)) &
                      ((pd.Timestamp("2024-12-31") - df["last_activity_date"]).dt.days > 30)).astype(int)
df["is_overdue"]   = ((df["stage"].isin(OPEN_STAGES)) &
                      (df["close_date"] < pd.Timestamp("2024-12-31"))).astype(int)
df["leakage_value"] = df["deal_value"] * df["is_overdue"]

print("Transformed: features engineered ✅")

# ── LOAD ──────────────────────────────────────────────────────

# Save clean CSV (this goes into Power BI)
df.to_csv("crm_clean.csv", index=False)

# Save to SQLite (this is where you run SQL queries)
conn = sqlite3.connect("crm_pipeline.db")
df.to_sql("opportunities", conn, if_exists="replace", index=False)

# Pre-aggregated tables for Power BI performance
STAGE_ORDER = ["Prospecting","Qualification","Needs Analysis","Value Proposition",
               "Decision Makers","Proposal/Price Quote","Negotiation/Review","Closed Won","Closed Lost"]

stage_summary = df.groupby("stage").agg(
    deal_count    = ("opportunity_id", "count"),
    total_value   = ("deal_value", "sum"),
    leakage_value = ("leakage_value", "sum"),
    stale_count   = ("is_stale", "sum"),
    won_count     = ("is_won", "sum"),
    avg_ttc       = ("time_to_close_days", "mean"),
).reset_index()
stage_summary["leakage_pct"] = (stage_summary["leakage_value"] / stage_summary["leakage_value"].sum() * 100).round(2)
stage_summary.to_sql("stage_summary", conn, if_exists="replace", index=False)

rep_perf = df.groupby(["rep_name", "rep_tier", "manager"]).agg(
    total_opps        = ("opportunity_id", "count"),
    total_pipeline    = ("deal_value", "sum"),
    closed_won        = ("is_won", "sum"),
    closed_lost       = ("is_lost", "sum"),
    avg_utilization   = ("rep_utilization_rate", "mean"),
    avg_forecast_gap  = ("forecast_gap_pct", "mean"),
    stale_deals       = ("is_stale", "sum"),
).reset_index()
rep_perf["win_rate"] = (rep_perf["closed_won"] / (rep_perf["closed_won"] + rep_perf["closed_lost"]).replace(0,1)).round(4)
rep_perf.to_sql("rep_performance", conn, if_exists="replace", index=False)

conn.close()

print("Loaded: crm_clean.csv + crm_pipeline.db ✅")
print(f"\n── KEY FINDINGS ──────────────────────────")
print(f"Total pipeline : ${df['deal_value'].sum():,.0f}")
print(f"Total leakage  : ${df['leakage_value'].sum():,.0f}")
print(f"Avg forecast gap: {df['forecast_gap_pct'].mean():.1f}%")
print(f"Stale deals    : {df['is_stale'].sum():,}")
print("\nTop 3 leakage stages:")
print(stage_summary.sort_values("leakage_value", ascending=False)[["stage","leakage_value","leakage_pct"]].head(3).to_string(index=False))