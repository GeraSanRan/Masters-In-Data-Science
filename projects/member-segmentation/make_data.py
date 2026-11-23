"""Generate a synthetic member table (seeded). Usage: python make_data.py"""
import numpy as np, pandas as pd
rng = np.random.default_rng(630)
n = 1500
seg = rng.choice(["regular", "casual", "social", "lapsing"], n, p=[0.28, 0.32, 0.22, 0.18])
p = {"regular": (14, 4, 30, 0.9), "casual": (4, 2, 12, 0.5), "social": (7, 3, 24, 0.2), "lapsing": (1.2, 1, 18, 0.4)}
rows = []
for s in seg:
    v, vs, ten, cls = p[s]
    visits = max(0, rng.normal(v, vs))
    rows.append(dict(visits_per_month=round(visits, 1), tenure_months=max(1, int(rng.normal(ten, 10))),
                     classes_per_month=round(max(0, rng.normal(cls * 3, 1.5)), 1),
                     guest_passes_per_month=round(max(0, rng.normal(1.5 if s == "social" else 0.2, 0.6)), 1),
                     avg_spend_per_month=round(max(0, rng.normal(55 + 3 * visits + (20 if s == "social" else 0), 12)), 2)))
d = pd.DataFrame(rows); d.insert(0, "member_id", [f"M{i:04d}" for i in range(1, n + 1)])
d.to_csv("data/members_behavior.csv", index=False)
