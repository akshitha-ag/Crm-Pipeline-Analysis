Salesforce CRM Pipeline & Services Utilization Analysis
Python · SQL · Power BI

About This Project
Orion Services is a fictional B2B SaaS company I created to simulate the CRM pipeline operations of a real professional services organization. The company has 50 sales reps across 4 regions selling 6 product lines.
I took on the role of Data Analyst for Orion Services. My manager asked me to analyze the sales pipeline and build an executive dashboard answering the following questions:

Where are we losing revenue in the pipeline? Identify which deal stages are bleeding the most money and prioritize intervention.
Why do our forecasts keep missing? Determine whether the forecast gap is a rep-level issue or a systemic process problem.
Are our reps productive or just busy? Segment reps by utilization vs win rate to find who's actually closing deals.
Is our pipeline growing or stagnating? Track quarter-over-quarter trends across 3 years.
Which products give us the best return on effort? Compare time-to-close against deal value across all product lines.

Dataset
52,000 Salesforce-style opportunity records spanning Jan 2022 – Dec 2024. Includes deal stage, rep, region, product, deal value, activity metrics, and forecast vs actual close rates. Data quality issues were intentionally introduced (inconsistent stage names, null values) to simulate real-world conditions.
Steps Taken

Data Generation: Built a Python script to generate 52K realistic CRM records with intentional data quality issues
ETL Pipeline: Standardized 21 stage name variants into 9, handled nulls, engineered 8 KPI features including weighted pipeline value, forecast gap, utilization rate, and leakage flags
SQL Analysis: Wrote 5 queries to answer each business question — leakage by stage, forecast gap by tier, rep segmentation, quarterly KPIs, and time-to-value
Power BI Dashboard: Built a 4-page interactive dashboard with slicers, DAX measures, and 30+ visuals presenting findings in exec-ready format

Key Findings

3 stages = 51% of all leakage — Prospecting, Qualification, and Needs Analysis are where deals die
10% forecast gap is systemic — consistent across Top, Mid, and Low rep tiers meaning the model needs fixing, not just the reps
Activity ≠ performance — highest win-rate reps actually have lower activity scores
Pipeline is flat — ~$200M/quarter for 12 straight quarters with no growth
Enterprise Suite = 10x ROI — $1,579 value per sales day vs $157 for Starter Pack, same close time

Dashboard

How to Run
bashpython generate_data.py
python etl_pipeline.py
python run_analysis.py
Open .pbix file in Power BI Desktop.

