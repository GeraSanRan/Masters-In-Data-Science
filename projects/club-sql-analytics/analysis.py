# %% [markdown]
# # Club analytics with SQL
# **Question.** Which plans earn the most, which lose members fastest, when is the club busiest, and who should staff call this week?
#
# **Data.** A synthetic SQLite database (`build_db.py`) with three tables: `members`, `visits`, and `payments`. All values are invented; no real member appears. The SQL lives in `queries.sql`; this notebook runs each query and charts a few.

# %%
import sqlite3, pandas as pd, matplotlib.pyplot as plt
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})
con = sqlite3.connect("club.db")
queries = [q.strip() for q in open("queries.sql").read().split(";") if "SELECT" in q]
pd.read_sql("SELECT (SELECT COUNT(*) FROM members) AS members, (SELECT COUNT(*) FROM visits) AS visits, (SELECT COUNT(*) FROM payments) AS payments", con)

# %% [markdown]
# ## Query 1: revenue by plan (active members)

# %%
q1 = pd.read_sql(queries[0], con); q1

# %% [markdown]
# ## Query 2: churn by plan

# %%
q2 = pd.read_sql(queries[1], con); q2

# %% [markdown]
# ## Query 3: busiest hours

# %%
q3 = pd.read_sql(queries[2], con).sort_values("hour")
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.bar(q3.hour.astype(str), q3.visits, color="#1f4e79"); ax.set_xlabel("Hour of day"); ax.set_title("Visits by hour")
plt.tight_layout(); plt.savefig("figures/hours.png"); plt.show()
q3

# %% [markdown]
# ## Query 4: engagement by status

# %%
pd.read_sql(queries[3], con)

# %% [markdown]
# ## Query 5: outreach list (active members quiet for 60+ days)

# %%
pd.read_sql(queries[4], con)

# %% [markdown]
# ## Notes
# * Joins (`members` to `payments` and `visits`), grouping, `HAVING`, and date arithmetic are all in `queries.sql`.
# * Revenue uses each member's plan fee at first payment, so it ignores discounts and price changes.
# * Synthetic data: the point is the SQL workflow, not the specific numbers.
