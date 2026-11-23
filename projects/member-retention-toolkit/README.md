# Member Retention Toolkit (DSC 680, Project 2)

An open, reusable notebook that finds members who are drifting away **before** they stop renewing, so staff can reach out while it still matters. It is built for recreational sports facilities and any other renewal-based membership organization.

> **All data here is synthetic.** The notebook generates its own demo tables, with planted patterns and realistic mess (duplicates, inconsistent labels, missing values, post-expiry visits), so the tool can be shared with no real member's information. Results show that the method works. They are **not** evidence about any real facility. Validate on your own past data before relying on it.

## What it does

1. **Cleans** a members table and a check-in table, and logs every change (counts of duplicates removed, labels fixed, rows set aside).
2. **Protects privacy** by dropping columns that look like personal data (names, emails, phones, addresses) and outputting anonymous IDs only.
3. **Checks readiness** and warns you if your data is too small, too unbalanced, or mis-mapped to trust.
4. **Compares four models** (majority baseline, logistic regression, random forest, XGBoost) with cross-validation, PR-AUC, a confusion matrix, and a fairness-by-plan table.
5. **Produces `at_risk_list.csv`**: a ranked list of anonymous IDs with a risk score and plain-language reasons. It is a prompt for friendly outreach by a person, never a reason to penalize a member.

## Use it with your own data (about 15 minutes)

1. Export two tables from your membership system: **members** (one row per member) and **visits** (one row per check-in).
2. In the notebook's settings cell, set `USE_DEMO_DATA = False`, point to your two CSV files, and map your column names in `COLS`.
3. Set your status words (`CHURNED_WORDS`, `RENEWED_WORDS`) and plan names (`PLAN_WORDS`).
4. Leave names, emails, phones, and addresses out of the files you load.
5. Run all cells and read the readiness report first.
6. Review `at_risk_list.csv` with staff. Keep a random holdout group so you can measure whether outreach actually raises renewals.

The notebook was tested by renaming every column and changing the renewal wording, editing only the settings cell. The results were identical.

## Run it

```bash
pip install -r requirements.txt
jupyter notebook retention_toolkit.ipynb   # then Run All; takes about a minute
```

## Files

| Path | What it is |
|---|---|
| `retention_toolkit.ipynb` | The runnable notebook (settings cell, cleaning, features, models, at-risk list, figures) |
| `paper/` | Draft white paper for Milestone 2, as PDF and Word |
| `figures/` | The five figures used in the paper |
| `outputs/at_risk_list.csv` | Sample tool output from the demo data |
| `outputs/results.json` | Every number reported in the paper |

## Demo results at a glance (synthetic data)

- Best model by cross-validation: logistic regression, test PR-AUC about 0.33 versus 0.22 for the baseline. That is a modest gain.
- It caught 119 of 171 test members who left (70%), but only about 30% of flagged members actually left, so most flags are false alarms. Plan-level error rates differ a lot, so check the fairness table before using the list.
- The tool recovered the strongest planted drivers (visit frequency, plan type, attendance trend).

*Provided as-is, with no warranty. Not legal advice. If you run it on real member data, you are responsible for privacy laws and your own policies.*
