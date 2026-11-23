# Membership Data Cleaning

**Problem.** A club-management system exports one messy file: a report title above the header, inconsistent group codes (`SIN`, `sin`, `Single`), duplicate people, impossible ages, and private contact details. Analysis cannot start until that is fixed, and privacy has to be protected.

**What is here (Python).**
| Script | What it does |
|---|---|
| `src/clean_memberships.py` | Strips whitespace and splits one export into a separate CSV per membership (command-line tool) |
| `src/clean_members.py` | Harmonizes group labels, removes duplicates, sets impossible ages to missing, drops contact details, and writes a change log |
| `src/anonymize_members.py` | De-identifies a raw export (replaces names and contact details with anonymous IDs) |
| `src/generate_synthetic_members.py` | Generates a fully synthetic export with the same problems, so the pipeline can be shared safely |

**Data.** `data/synthetic_members.csv` is fully synthetic (7,320 rows; emails on `example.com`, phones in the fictional 555-01XX block). No real member appears in this repository. `outputs/members_clean.csv` and its `.log.json` show the result and the counts of every change.

**Run it.**
```bash
python src/generate_synthetic_members.py data/synthetic_members.csv
python src/clean_members.py data/synthetic_members.csv outputs/members_clean.csv
```
The cleaned file feeds `../member-retention-prediction/`.

**Limits.** Written for one club's export format; other systems need column names adjusted.
