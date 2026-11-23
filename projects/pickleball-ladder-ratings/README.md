# Pickleball Ladder Ratings (personal project, simulation)

**Question.** On a ladder day where winners move up a court and losers move down, does the final order match true skill? Does an Elo rating do better?

**Method.** Simulation: 24 players with hidden skill, 6 courts of 4, round-robin games, 300 simulated events per round count. Compare the final ladder order and the Elo rating with true skill (Spearman correlation).

**Result.** After 1 round, Elo matches skill much better (0.65 vs 0.25). By about 6 rounds the two are about equal (0.86 vs 0.85), and by 8 rounds both are near 0.87. For short events, ratings from past results sort players faster; a long ladder day sorts well on its own.

**Files.** `ladder_ratings.ipynb` (executed), `analysis.py`, `figures/`.
**Limits.** Simplified model: assumed win-probability curve, singles-style round robins, no doubles partners, no-shows or injuries. Not data from a real event.
