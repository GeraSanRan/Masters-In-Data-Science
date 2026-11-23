# The NBA Three-Point Revolution: Before and After Stephen Curry

**Question.** Did the league-wide three-point shooting percentage rise after Stephen Curry entered the NBA in 2009-10, and what actually changed?

**Short answer.** Not much in *percentage*, a lot in *volume*.

| Measure (league average per season) | 1997-98 to 2008-09 | 2009-10 to 2025-26 |
|---|---|---|
| 3-point percentage | 35.4% | 35.8% (+0.4 pts, 95% interval about 0.0 to +0.9) |
| 3-point attempts per game | 15.2 | 28.1 (about 1.85x) |

- The percentage was already rising before 2009 and flattened afterward (segmented regression, slope change p < 0.01).
- Attempts grew about 0.5 per game per year before 2009 and about 1.4 per year after (slope change p < 0.001).
- Curry himself shot about 42% on high volume, roughly 7 points above the league in seasons with 50+ games.

## Limits
This is a before/after comparison of season averages, so it does **not** show that Curry caused the change. Analytics adoption, the 2004 hand-checking rule change, coaching, and player development all moved during the same years. Per-game counts are rounded to one decimal in the source.

## Files
| Path | What it is |
|---|---|
| `nba_three_point_analysis.ipynb` | Executed notebook: windows, Welch t-test, bootstrap interval, segmented regression, Curry comparison |
| `analysis.py` | Same analysis as a script with cell markers |
| `data/league_3pt_by_season.csv` | League per-game 3P, 3PA, 3P%, FG%, pace, games, 1979-80 to 2025-26 |
| `data/curry_3pt_by_season.csv` | Curry per-game 3P, 3PA, 3P%, FG% by season, 2009-10 to 2025-26 |
| `figures/` | Three charts used above |
| `results.json` | Every number reported here |

## Run it
```bash
pip install -r requirements.txt
jupyter notebook nba_three_point_analysis.ipynb   # Run All
```

## Data source
Basketball-Reference, league per-game table (https://www.basketball-reference.com/leagues/NBA_stats_per_game.html) and Stephen Curry's player page (https://www.basketball-reference.com/players/c/curryst01.html), retrieved November 2026. The 2026-27 season is partial and excluded. Re-check values against the source before relying on them.
