import sqlite3
import pandas as pd

conn = sqlite3.connect("crm_pipeline.db")

def run(title, sql):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    print(pd.read_sql(sql, conn).to_string(index=False))

# ── QUERY 1: Revenue Leakage by Stage ─────────────────────────
# This answers: which stages are bleeding the most money?
run("1. REVENUE LEAKAGE BY STAGE", """
    SELECT
        stage,
        deal_count,
        ROUND(total_value / 1e6, 1)     AS pipeline_M,
        ROUND(leakage_value / 1e6, 1)   AS leakage_M,
        leakage_pct,
        CASE
            WHEN leakage_pct >= 18 THEN 'CRITICAL - Act Now'
            WHEN leakage_pct >= 14 THEN 'HIGH - Monitor Closely'
            ELSE 'MEDIUM'
        END AS priority
    FROM stage_summary
    ORDER BY leakage_value DESC
""")

# ── QUERY 2: Forecast vs Actual Gap by Rep Tier ───────────────
# This answers: who is over-promising and under-delivering?
run("2. FORECAST GAP BY REP TIER", """
    SELECT
        rep_tier,
        COUNT(*)                                AS total_deals,
        ROUND(AVG(forecast_close_rate)*100, 1)  AS avg_forecast_pct,
        ROUND(AVG(actual_close_rate)*100, 1)    AS avg_actual_pct,
        ROUND(AVG(forecast_gap_pct), 1)         AS avg_gap_pct
    FROM opportunities
    GROUP BY rep_tier
    ORDER BY avg_gap_pct DESC
""")

# ── QUERY 3: Rep Utilization Segmentation ─────────────────────
# This answers: which reps are busy but ineffective vs efficient closers?
run("3. REP UTILIZATION SEGMENTS (TOP 15)", """
    SELECT
        rep_name,
        rep_tier,
        total_opps,
        ROUND(avg_utilization, 3)           AS utilization_rate,
        ROUND(win_rate * 100, 1)            AS win_rate_pct,
        stale_deals,
        CASE
            WHEN avg_utilization > 1.5 AND win_rate > 0.55 THEN 'High Performer'
            WHEN avg_utilization > 1.5 AND win_rate <= 0.55 THEN 'Busy but Ineffective'
            WHEN avg_utilization <= 1.5 AND win_rate > 0.55 THEN 'Efficient Closer'
            ELSE 'Needs Coaching'
        END AS segment
    FROM rep_performance
    ORDER BY win_rate DESC
    LIMIT 15
""")

# ── QUERY 4: Period over Period KPIs ──────────────────────────
# This answers: is the pipeline growing or shrinking quarter by quarter?
run("4. QUARTERLY PIPELINE TRENDS", """
    SELECT
        fiscal_year,
        fiscal_quarter,
        COUNT(*)                            AS total_deals,
        ROUND(SUM(deal_value)/1e6, 1)       AS pipeline_M,
        ROUND(AVG(deal_value), 0)           AS avg_deal_size,
        SUM(is_won)                         AS closed_won,
        ROUND(AVG(time_to_close_days), 1)   AS avg_days_to_close,
        ROUND(AVG(forecast_gap_pct), 1)     AS avg_forecast_gap
    FROM opportunities
    GROUP BY fiscal_year, fiscal_quarter
    ORDER BY fiscal_year, fiscal_quarter
""")

# ── QUERY 5: Time-to-Value by Product ─────────────────────────
# This answers: which products close fastest with highest value?
run("5. TIME TO VALUE BY PRODUCT", """
    SELECT
        product,
        COUNT(*)                                        AS deals,
        ROUND(AVG(deal_value), 0)                       AS avg_deal_value,
        ROUND(AVG(time_to_close_days), 1)               AS avg_days_to_close,
        ROUND(AVG(deal_value)/AVG(time_to_close_days))  AS value_per_day,
        ROUND(SUM(is_won)*100.0/COUNT(*), 1)            AS win_rate_pct
    FROM opportunities
    GROUP BY product
    ORDER BY value_per_day DESC
""")

conn.close()
print("\n✅ Analysis complete")