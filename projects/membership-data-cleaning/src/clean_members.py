"""Clean a club-member export for retention analysis.

Steps (each logged with counts only, never personal data):
  1. Find the real header row (exports often put a report title above it).
  2. Strip whitespace, drop blank rows.
  3. Harmonize membership group codes/labels (SIN, sin, Single -> "Single").
  4. Flag and drop duplicate people (same name + email/phone).
  5. Check ages; set impossible values to missing (kept, not guessed).
  6. Drop direct identifiers (names, emails, phones). Only an anonymous
     member_id, age, status, and group are written.

Usage:  python src/clean_members.py data/synthetic_members.csv outputs/members_clean.csv
Writes: the clean CSV and <out>.log.json (the data-change log).
"""
import csv, hashlib, json, re, sys

HEADER_KEY = "First name"
# Raw label (lower-case, trimmed) -> (clean label, segment)
GROUP_MAP = {
    "sin": ("Single", "Member"), "single": ("Single", "Member"),
    "fam": ("Family", "Member"), "family": ("Family", "Member"),
    "cou": ("Couple", "Member"), "couple": ("Couple", "Member"),
    "jr": ("Junior", "Member"), "junior": ("Junior", "Member"),
    "senior single": ("Senior Single", "Member"),
    "monthly senior singles": ("Senior Single (Monthly)", "Member"),
    "monthly senior couple": ("Senior Couple (Monthly)", "Member"),
    "guest member": ("Guest", "Non-member"), "guest": ("Guest", "Non-member"),
}
VALID_AGE = (5, 100)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def digits(s):
    return re.sub(r"\D", "", s or "")


def main(src, out):
    log = {}
    with open(src, newline="", encoding="utf-8-sig") as f:
        raw = list(csv.reader(f))
    start = next(i for i, r in enumerate(raw) if HEADER_KEY in [c.strip() for c in r])
    header = [c.strip() for c in raw[start]]
    rows = [{h: c.strip() for h, c in zip(header, r)} for r in raw[start + 1:] if any(c.strip() for c in r)]
    log["rows_read"] = len(rows)

    seen, kept, unmapped = set(), [], {}
    dup = bad_age = 0
    for r in rows:
        key = (norm(r["First name"]), norm(r["Last name"]), norm(r["Email"]) or digits(r["Phone (Cell)"])[-7:])
        if key in seen:
            dup += 1
            continue
        seen.add(key)
        label = GROUP_MAP.get(r["User Group Name"].lower().strip())
        if label is None:
            unmapped[r["User Group Name"]] = unmapped.get(r["User Group Name"], 0) + 1
            label = ("Unmapped", "Unknown")
        try:
            age = int(float(r["Age"]))
            if not VALID_AGE[0] <= age <= VALID_AGE[1]:
                raise ValueError
        except ValueError:
            age, bad_age = "", bad_age + 1
        mid = hashlib.sha256("|".join(key).encode()).hexdigest()[:10]
        kept.append({"member_id": "M" + mid, "age": age, "status": r["Member Status"],
                     "group": label[0], "segment": label[1]})

    log.update(duplicates_dropped=dup, ages_set_to_missing=bad_age,
               unmapped_group_labels=unmapped, rows_written=len(kept),
               columns_dropped=["First name", "Last name", "Email", "Phone (Cell)", "Phone (Home)"])
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["member_id", "age", "status", "group", "segment"])
        w.writeheader()
        w.writerows(kept)
    with open(out + ".log.json", "w") as f:
        json.dump(log, f, indent=2)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
