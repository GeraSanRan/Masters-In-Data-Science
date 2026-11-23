"""Generate a fully synthetic club-member export for demonstrating the pipeline.

Nothing here comes from real people. Names are random combinations, emails use
the reserved domain example.com, and phones use the 555-01XX block reserved for
fiction. The file mimics the layout and the messiness of a real club-management
export: a report title above the header, inconsistent group labels (SIN / sin /
Single), duplicate people, and a few impossible ages.

NOTE: Retention differs by group by construction (see STATUS_PROBS), so any
model "finding" on this file shows the pipeline works, not something about a
real club.

Usage:  python src/generate_synthetic_members.py data/synthetic_members.csv
"""
import csv, random, sys

random.seed(680)
N = 7200
FIRST = "Alex Jordan Taylor Morgan Casey Riley Jamie Avery Quinn Parker Reese Rowan Skyler Dakota Emerson Finley Harper Hayden Kendall Logan Mason Noel Peyton Sage Blake Cameron Drew Ellis Gray Jesse Kai Lane Maya Noah Priya Omar Lena Ravi Sofia Mateo".split()
LAST = "Alder Bennett Calloway Dalton Everett Fairbanks Garrison Holloway Ingram Jennings Kensington Lockhart Maddox Northcott Oakley Prescott Quimby Radcliffe Sterling Thornton Underhill Vance Whitaker Yardley Ashford Brighton Carmichael Devereux Eastwood Fenwick Gladstone Okafor Nguyen Patel Rivera".split()
# (label spellings, weight, age range)
GROUPS = [(["SIN", "Single", "sin"], 30, (18, 70)), (["FAM", "Family", "fam "], 20, (28, 60)),
          (["COU", "Couple"], 10, (25, 75)), (["Jr", "Junior"], 8, (8, 17)),
          (["Senior Single"], 7, (60, 85)), (["Monthly Senior Singles"], 4, (60, 85)),
          (["Monthly Senior Couple"], 3, (60, 85)), (["Guest member", "Guest Member"], 18, (14, 80))]
# P(Active, Expired, Canceled, On Hold)
STATUS_PROBS = {"FAM": [.22, .45, .10, .08], "SIN": [.25, .50, .10, .08]}
DEFAULT_PROBS = [.45, .30, .07, .06]


def pick_status(label):
    if label.lower().startswith("guest"):
        return "Non-member"
    probs = STATUS_PROBS.get(label.strip().upper(), DEFAULT_PROBS)
    r, c = random.random(), 0
    for name, p in zip(["Active", "Expired", "Canceled", "On Hold"], probs):
        c += p
        if r < c:
            return name
    return "Expired"


def phone():
    return f"({random.randint(201, 989)}) 555-01{random.randint(0, 99):02d}"


def main(out):
    rows = []
    for _ in range(N):
        labels, _, (lo, hi) = random.choices(GROUPS, [g[1] for g in GROUPS])[0]
        label = random.choice(labels)
        first, last = random.choice(FIRST), random.choice(LAST)
        age = random.randint(lo, hi)
        if random.random() < .004:
            age = random.choice([0, -1, 120, 150, ""])
        email = f"{first}.{last}{random.randint(1, 999)}@example.com".lower() if random.random() < .8 else ""
        rows.append([first, last, age, email, phone() if random.random() < .85 else "",
                     phone() if random.random() < .2 else "", pick_status(label), label])
    rows += [list(random.choice(rows)) for _ in range(120)]  # duplicate people
    random.shuffle(rows)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Users_HC"] + [""] * 7)  # report title row, as in the real export
        w.writerow(["First name", "Last name", "Age", "Email", "Phone (Cell)",
                    "Phone (Home)", "Member Status", "User Group Name"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} synthetic rows to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/synthetic_members.csv")
