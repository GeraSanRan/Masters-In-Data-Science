# Club Analytics with SQL (personal project)

**Question.** Which plans earn the most, which lose members fastest, when is the club busiest, and who needs outreach?

**Data.** Synthetic SQLite database `club.db` (800 members, about 26,000 visits, 800 payments) built by `build_db.py`. No real member appears.

**What is here.** Five queries in `queries.sql` using joins, grouping, `HAVING`, and date arithmetic, run and shown in `club_analytics.ipynb`.

**Findings on the synthetic data.** Family plans bring in the most monthly revenue ($11,990 from 109 active members) but also churn most (42%). Visits peak at 6 PM, followed by 5 PM and 7 PM. Active members visit about 3.7 times a month versus about 1.1 to 1.2 for canceled and expired members. The last query lists active members with no visit in 60 days.

**Run.** `python build_db.py`, then open the notebook.
**Limits.** Revenue uses each member's first plan fee and ignores discounts and price changes.
