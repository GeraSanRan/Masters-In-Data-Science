"""Generate synthetic court bookings (seeded). Usage: python make_data.py"""
import numpy as np, pandas as pd
rng = np.random.default_rng(630)
days = pd.date_range("2026-01-05", periods=26 * 7)
rows = []
for d in days:
    for h in range(6, 22):
        base = 4
        if d.dayofweek < 5: base += 8 * np.exp(-((h - 18.5) ** 2) / 4) + 3 * np.exp(-((h - 7) ** 2) / 3)
        else: base += 9 * np.exp(-((h - 10) ** 2) / 6) + 3 * np.exp(-((h - 15) ** 2) / 8)
        base *= 1 + 0.12 * np.sin(2 * np.pi * (d - days[0]).days / 180)
        rows.append((d.date(), h, int(np.clip(rng.poisson(base), 0, 12))))
pd.DataFrame(rows, columns=["date", "hour", "courts_booked"]).to_csv("data/court_bookings.csv", index=False)
