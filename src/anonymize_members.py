"""
anonymize_members.py

De-identify a club-management member export so it can be shared, committed to
GitHub, or analyzed in a public portfolio.

What it does
------------
* Flags likely duplicate people using the REAL name/email/phone, *before*
  anything is replaced (so duplicates are not hidden by anonymization).
* Replaces names, emails, and phone numbers with synthetic values:
    - emails use the reserved domain example.com
    - phones use the 555-01XX block that is reserved for fictional use
* Gives each person a stable pseudonymous member_id. Rows that are the same
  real person receive the same fake identity.
* Keeps the analysis fields (age, status, group) exactly as they are.
* Writes a data-change log (counts only, no personal data).

Usage
-----
    python anonymize_members.py RAW.csv members_anonymized.csv --salt "any-secret-text"

Keep RAW.csv and the salt OFF GitHub (add them to .gitignore). Only the
anonymized output should ever be shared.

Standard library only; no installs required.
"""

import argparse
import csv
import hashlib
import random
import re
import sys
from collections import Counter

# Column names as exported by the club software. Edit if yours differ.
COLS = {
    "first": "First name",
    "last": "Last name",
    "email": "Email",
    "phone_cell": "Phone (Cell)",
    "phone_home": "Phone (Home)",
}
KEEP_AS_IS = ["Age", "Member Status", "User Group Name"]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery",
    "Quinn", "Parker", "Reese", "Rowan", "Skyler", "Dakota", "Emerson", "Finley",
    "Harper", "Hayden", "Kendall", "Logan", "Mason", "Noel", "Peyton", "Sage",
    "Blake", "Cameron", "Drew", "Ellis", "Gray", "Jesse", "Kai", "Lane",
]
LAST_NAMES = [
    "Alder", "Bennett", "Calloway", "Dalton", "Everett", "Fairbanks", "Garrison",
    "Holloway", "Ingram", "Jennings", "Kensington", "Lockhart", "Maddox",
    "Northcott", "Oakley", "Prescott", "Quimby", "Radcliffe", "Sterling",
    "Thornton", "Underhill", "Vance", "Whitaker", "Yardley", "Ashford",
    "Brighton", "Carmichael", "Devereux", "Eastwood", "Fenwick", "Gladstone",
]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def digits(s):
    return re.sub(r"\D", "", s or "")


def person_key(row):
    """Best available real-world identity key, used only to group duplicates."""
    email = norm(row.get(COLS["email"]))
    if email:
        return "e:" + email
    name = norm(row.get(COLS["first"])) + "|" + norm(row.get(COLS["last"]))
    phone = digits(row.get(COLS["phone_cell"])) or digits(row.get(COLS["phone_home"]))
    return "n:" + name + "|" + phone[-7:]


def seeded(key, salt):
    h = hashlib.sha256((salt + "|" + key).encode()).hexdigest()
    return random.Random(int(h[:16], 16)), h[:10]


def fake_phone(rng):
    area = rng.choice([a for a in range(201, 990) if a % 100 != 11])
    return f"({area}) 555-01{rng.randint(0, 99):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_csv")
    ap.add_argument("out_csv")
    ap.add_argument("--salt", required=True, help="secret text; do not commit it")
    args = ap.parse_args()

    with open(args.raw_csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = reader.fieldnames or []

    missing = [c for c in list(COLS.values()) + KEEP_AS_IS if c not in header]
    if missing:
        sys.exit(f"Missing expected columns: {missing}\nFound: {header}\n"
                 "Edit COLS / KEEP_AS_IS at the top of this script.")

    keys = [person_key(r) for r in rows]
    counts = Counter(keys)

    out_fields = ["member_id", "first_name", "last_name", "email",
                  "phone_cell", "phone_home"] + KEEP_AS_IS + \
                 ["records_for_this_person", "is_duplicate_record"]
    seen = set()
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for r, k in zip(rows, keys):
            rng, mid = seeded(k, args.salt)
            first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
            has_cell = bool(digits(r.get(COLS["phone_cell"])))
            has_home = bool(digits(r.get(COLS["phone_home"])))
            has_email = bool(norm(r.get(COLS["email"])))
            dup = k in seen
            seen.add(k)
            out = {
                "member_id": "M" + mid,
                "first_name": first,
                "last_name": last,
                "email": f"{first}.{last}.{mid[:6]}@example.com".lower() if has_email else "",
                "phone_cell": fake_phone(rng) if has_cell else "",
                "phone_home": fake_phone(rng) if has_home else "",
                "records_for_this_person": counts[k],
                "is_duplicate_record": int(dup),
            }
            for c in KEEP_AS_IS:
                out[c] = r.get(c, "")
            w.writerow(out)

    n_dup = sum(1 for k in counts if counts[k] > 1)
    print(f"Rows read:                {len(rows)}")
    print(f"Distinct people:          {len(counts)}")
    print(f"People with 2+ records:   {n_dup}")
    print(f"Extra (duplicate) rows:   {len(rows) - len(counts)}")
    print(f"Wrote anonymized file:    {args.out_csv}")
    print("Reminder: keep the raw file and the salt out of GitHub.")


if __name__ == "__main__":
    main()
