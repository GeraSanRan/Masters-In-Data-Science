"""Build a small synthetic club database in SQLite (seeded). Usage: python build_db.py"""
import sqlite3, numpy as np, pandas as pd
rng = np.random.default_rng(630)
n = 800
plans = {"Single": 55, "Family": 110, "Couple": 90, "Junior": 30, "Senior": 40}
pm = rng.choice(list(plans), n, p=[0.35, 0.22, 0.15, 0.1, 0.18])
start = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 600, n), unit="D")
status = rng.choice(["active", "expired", "canceled"], n, p=[0.6, 0.28, 0.12])
members = pd.DataFrame({"member_id": range(1, n + 1), "plan": pm, "start_date": start.date, "status": status})
visits = []
for mid, st, s in zip(members.member_id, members.status, start):
    rate = 0.35 if st == "active" else 0.12
    for d in range(0, 600, 1):
        day = s + pd.Timedelta(days=d)
        if day > pd.Timestamp("2026-10-31"): break
        if rng.random() < rate / 3:
            visits.append((mid, day.date(), int(rng.choice([7, 8, 9, 12, 17, 18, 19, 20], p=[.08, .1, .1, .1, .17, .2, .15, .1]))))
visits = pd.DataFrame(visits, columns=["member_id", "visit_date", "hour"])
pay = [(m, p, plans[p], s.date()) for m, p, s in zip(members.member_id, members.plan, start)]
payments = pd.DataFrame(pay, columns=["member_id", "plan", "monthly_fee", "first_payment_date"])
con = sqlite3.connect("club.db")
for name, df in [("members", members), ("visits", visits), ("payments", payments)]:
    df.to_sql(name, con, if_exists="replace", index=False)
con.close()
