# Member Retention Prediction (Recreational Sports Club)

**Problem.** Which members are likely to be retained, and which membership groups are at risk? Retention drives revenue, staffing, and scheduling.

**Data.** `data/synthetic_members.csv`: 7,320 fully synthetic rows that reproduce the layout and the problems of a real club-management export I cleaned at work (report title above the header, inconsistent group codes such as `SIN`/`sin`/`Single`, duplicate people, impossible ages). No real member data is in this repository. Retention differs by group by construction, so results demonstrate the pipeline, not a real club.

**Methods.** Cleaning script (`src/clean_members.py`) with a change log; stratified train/test split; logistic regression, decision tree, and random forest with class weights; accuracy, precision, recall, F1, ROC-AUC, and 5-fold cross-validation against a majority-class baseline; fairness check by age band; sensitivity check on the retention label.

**Results (this run, synthetic data).**
- Family and Single groups are retained least (about 33% and 35%).
- Best test ROC-AUC is about 0.59 versus 0.50 baseline: a weak screen, not strong enough for individual decisions.
- The fairness check shows large gaps across age bands, because age is tangled with membership group.

**Tools.** Python, pandas, scikit-learn, matplotlib, Jupyter.

**Run it.** `pip install pandas scikit-learn matplotlib seaborn`, then run `notebooks/member_retention.ipynb` from the repository root. It regenerates the data, runs the cleaning, and writes figures and tables to `outputs/`.

**Files.** `notebooks/member_retention.ipynb`, `src/generate_synthetic_members.py`, `src/clean_members.py`, `src/anonymize_members.py` (for de-identifying a real export), `outputs/`.
