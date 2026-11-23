# Club Operations Dashboard (personal project)

A one-page dashboard built from the synthetic database in `../club-sql-analytics/`: four KPI tiles (active members, monthly recurring revenue, churn, visits in the last 30 days) and four charts (visits per month, revenue by plan, churn by plan, visits by hour).

**Files.** `build_dashboard.py` builds `dashboard.html` (open in any browser; the charts are embedded) and `dashboard.png`.
**Run.** Run `python build_db.py` in `club-sql-analytics`, then `python build_dashboard.py` here.
**Limits.** Synthetic data. Visits per month climb because members join over time in the generated data, which is a quirk of the simulation and not a real trend. Charts are static images, not interactive filters.
