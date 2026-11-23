# Member Segmentation (personal project)

**Question.** Are there distinct kinds of members based on how they use a club?

**Data.** Synthetic table of 1,500 members (visits, tenure, classes, guest passes, spend) from `make_data.py`. Four groups are planted in the data; no real member appears.

**Method.** Standardize features, run k-means for k = 2 to 8, pick k by silhouette score, profile each cluster, plot with PCA.

**Result.** Silhouette picked k = 3: a core group (26% of members, about 14 visits and 3 classes a month, highest spend), a low-engagement group (52%, about 3 visits a month, the likely retention risk), and a social group (22%, about 7 visits a month and the most guest passes). The method merged two of the four planted groups, so segment counts from the algorithm are a starting point, not a truth.

**Files.** `member_segmentation.ipynb` (executed), `analysis.py`, `make_data.py`, `data/members_behavior.csv`, `figures/`.
**Limits.** Synthetic data. Real clubs will show messier segments. Use results for friendly outreach, never to penalize members.
