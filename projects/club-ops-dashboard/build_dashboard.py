"""Build a one-page club operations dashboard from the synthetic club database.
Usage: python build_dashboard.py   (reads ../club-sql-analytics/club.db, writes dashboard.html and dashboard.png)"""
import sqlite3, base64, io, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})
con = sqlite3.connect("../club-sql-analytics/club.db")
members = pd.read_sql("SELECT * FROM members", con, parse_dates=["start_date"])
visits = pd.read_sql("SELECT * FROM visits", con, parse_dates=["visit_date"])
pay = pd.read_sql("SELECT * FROM payments", con)

active = members[members.status == "active"]
mrr = pay[pay.member_id.isin(active.member_id)].monthly_fee.sum()
churn = (members.status != "active").mean() * 100
v30 = visits[visits.visit_date > visits.visit_date.max() - pd.Timedelta(days=30)]
kpis = [("Active members", f"{len(active):,}"), ("Monthly recurring revenue", f"${mrr:,.0f}"),
        ("Churn (expired + canceled)", f"{churn:.0f}%"), ("Visits, last 30 days", f"{len(v30):,}")]

fig, ax = plt.subplots(2, 2, figsize=(11, 6.5))
visits["month"] = visits.visit_date.dt.to_period("M").dt.to_timestamp()
m = visits.groupby("month").size(); m = m[m.index < m.index.max()]  # drop partial last month if any
ax[0, 0].plot(m.index, m.values, color="#1f4e79", lw=2); ax[0, 0].set_title("Visits per month"); ax[0, 0].tick_params(axis="x", rotation=30)
rev = pay[pay.member_id.isin(active.member_id)].merge(members[["member_id"]], on="member_id").groupby("plan").monthly_fee.sum().sort_values()
ax[0, 1].barh(rev.index, rev.values, color="#1f4e79"); ax[0, 1].set_title("Monthly revenue by plan (active)")
ch = members.groupby("plan").status.apply(lambda s: (s != "active").mean() * 100).sort_values()
ax[1, 0].barh(ch.index, ch.values, color="#c0392b"); ax[1, 0].set_title("Churn % by plan")
h = visits.groupby("hour").size()
ax[1, 1].bar(h.index.astype(str), h.values, color="#1f4e79"); ax[1, 1].set_title("Visits by hour of day")
plt.tight_layout(); plt.savefig("dashboard.png")
buf = io.BytesIO(); plt.savefig(buf, format="png"); b64 = base64.b64encode(buf.getvalue()).decode()

tiles = "".join(f'<div class="tile"><div class="v">{v}</div><div class="k">{k}</div></div>' for k, v in kpis)
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Club operations dashboard (synthetic data)</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem auto;max-width:1000px;padding:0 1rem;color:#222}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1rem 0}}
.tile{{border:1px solid #ddd;border-radius:8px;padding:1rem}}.v{{font-size:1.8rem;font-weight:700;color:#1f4e79}}.k{{color:#555}}
img{{max-width:100%}}.note{{color:#555;font-size:.9rem}}</style></head><body>
<h1>Club operations dashboard</h1><p class="note">Synthetic data. No real member appears.</p>
<div class="tiles">{tiles}</div><img alt="Four charts: visits per month, revenue by plan, churn by plan, visits by hour" src="data:image/png;base64,{b64}">
</body></html>"""
open("dashboard.html", "w").write(html)
print(kpis)
