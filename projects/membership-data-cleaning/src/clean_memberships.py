#!/usr/bin/env python3
"""Clean a CSV and export one file per specified membership.

This script reads a source CSV, removes blank/extra whitespace, and writes a
separate CSV for each membership you list in --memberships.

Example:
    python clean_memberships.py \
      --input members.csv \
      --membership-column Membership \
      --memberships "Gold,Silver,Bronze" \
      --output-dir cleaned_memberships
"""

import argparse
import csv
import os
import re


def clean_value(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_membership(value):
    cleaned = clean_value(value)
    return " ".join(cleaned.lower().split())


def slugify(value):
    value = clean_value(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "membership"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f"CSV file '{path}' does not contain a header row.")

        fieldnames = [clean_value(field) for field in reader.fieldnames]
        rows = []

        for row in reader:
            cleaned_row = {}
            for key, value in row.items():
                cleaned_row[clean_value(key)] = clean_value(value)
            if any(cleaned_row.values()):
                rows.append(cleaned_row)

        return fieldnames, rows


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_by_membership(input_path, membership_column, memberships, output_dir):
    fieldnames, rows = read_csv(input_path)

    if membership_column not in fieldnames:
        raise ValueError(
            f"Membership column '{membership_column}' not found. Available columns: {fieldnames}"
        )

    allowed_memberships = [clean_value(item) for item in memberships]
    normalized_lookup = {
        normalize_membership(name): name for name in allowed_memberships if clean_value(name)
    }

    grouped_rows = {name: [] for name in allowed_memberships}
    missing_rows = []

    for row in rows:
        member_value = row.get(membership_column, "")
        normalized_member = normalize_membership(member_value)

        if not normalized_member:
            missing_rows.append(row)
            continue

        if normalized_member in normalized_lookup:
            group_name = normalized_lookup[normalized_member]
            grouped_rows[group_name].append(row)
        else:
            missing_rows.append(row)

    os.makedirs(output_dir, exist_ok=True)

    for membership_name, group in grouped_rows.items():
        output_path = os.path.join(output_dir, f"{slugify(membership_name)}.csv")
        write_csv(output_path, fieldnames, group)

    if missing_rows:
        missing_path = os.path.join(output_dir, "missing_memberships.csv")
        write_csv(missing_path, fieldnames, missing_rows)

    print(f"Created files for memberships: {', '.join(allowed_memberships) if allowed_memberships else 'none'}")
    print(f"Output folder: {output_dir}")

    return grouped_rows


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split one CSV file into separate CSV files by membership type."
    )
    parser.add_argument("--input", required=True, help="Path to the source CSV file")
    parser.add_argument(
        "--membership-column",
        required=True,
        help="Name of the column that contains membership values",
    )
    parser.add_argument(
        "--memberships",
        required=True,
        help="Comma-separated list of memberships to create, for example: Gold,Silver,Bronze",
    )
    parser.add_argument(
        "--output-dir",
        default="./cleaned_memberships",
        help="Folder where the membership CSV files will be saved",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    membership_names = [name.strip() for name in args.memberships.split(",") if name.strip()]
    split_by_membership(
        input_path=args.input,
        membership_column=args.membership_column,
        memberships=membership_names,
        output_dir=args.output_dir,
    )
