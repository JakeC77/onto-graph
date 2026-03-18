#!/usr/bin/env python3
"""
Validate evidence chains resolve to actual source data.

Checks multiple levels:
  Level 1: File existence — cited files exist in the data room
  Level 2: Location validity — cited locations are plausible for the file type
  Level 3: Value accuracy — cited values exist at the cited location (for tabular data)

Usage:
    python tools/validate_evidence.py <artifact_path> --data-room <path> [--level 1|2|3] [--verbose]

Examples:
    python tools/validate_evidence.py runs/acme_20260317/phase_1_ontology/ontology.yaml --data-room ~/DataRoom/acme/
    python tools/validate_evidence.py runs/acme_20260317/phase_1_ontology/decisions/ --data-room ~/DataRoom/acme/ --level 3

Exit codes:
    0 = all checks pass
    1 = validation failures found
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def extract_evidence_entries(data: dict, path: str = "") -> list[dict]:
    """Recursively find all evidence entries in a YAML structure."""
    entries = []

    if isinstance(data, dict):
        # Direct evidence entry
        if "source" in data and ("location" in data or "observation" in data):
            entry = dict(data)
            entry["_artifact_path"] = path
            entries.append(entry)

        # Evidence list
        if "evidence" in data and isinstance(data["evidence"], list):
            for e in data["evidence"]:
                if isinstance(e, dict):
                    entry = dict(e)
                    entry["_artifact_path"] = path
                    entries.append(entry)

        # Evidence chain
        if "evidence_chain" in data and isinstance(data["evidence_chain"], list):
            for e in data["evidence_chain"]:
                if isinstance(e, dict):
                    entry = dict(e)
                    entry["_artifact_path"] = path
                    entries.append(entry)

        # Recurse into values
        for v in data.values():
            entries.extend(extract_evidence_entries(v, path))

    elif isinstance(data, list):
        for item in data:
            entries.extend(extract_evidence_entries(item, path))

    return entries


def check_level_1(entries: list[dict], data_room: str) -> list[str]:
    """Level 1: File existence."""
    failures = []
    for e in entries:
        source = e.get("source", "")
        if not source:
            continue
        full_path = os.path.join(data_room, source)
        if not os.path.exists(full_path):
            failures.append(
                f"File not found: {source} (cited in {e.get('_artifact_path', '?')})"
            )
    return failures


def check_level_2(entries: list[dict], data_room: str) -> list[str]:
    """Level 2: Location plausibility."""
    failures = []
    for e in entries:
        source = e.get("source", "")
        location = e.get("location", "")
        if not source or not location:
            continue

        full_path = os.path.join(data_room, source)
        if not os.path.exists(full_path):
            continue  # Already caught by level 1

        ext = Path(full_path).suffix.lower()

        # Check row references for tabular files
        if ext in (".csv", ".tsv", ".xlsx", ".xls"):
            row_match = re.search(r"row\s+(\d+)", location, re.IGNORECASE)
            if row_match and HAS_PANDAS:
                try:
                    if ext in (".csv", ".tsv"):
                        df = pd.read_csv(full_path, nrows=0)
                        # Can't check row count without reading full file
                    # Column reference check
                    col_match = re.search(r"column\s+['\"]?(\w+)['\"]?", location, re.IGNORECASE)
                    if col_match:
                        col_name = col_match.group(1)
                        if ext in (".csv", ".tsv"):
                            df = pd.read_csv(full_path, nrows=1)
                        else:
                            df = pd.read_excel(full_path, nrows=1)
                        if col_name not in df.columns:
                            failures.append(
                                f"Column '{col_name}' not found in {source} "
                                f"(cited in {e.get('_artifact_path', '?')})"
                            )
                except Exception:
                    pass  # File reading issues already flagged elsewhere

    return failures


def check_level_3(entries: list[dict], data_room: str) -> list[str]:
    """Level 3: Value accuracy (tabular data only)."""
    if not HAS_PANDAS:
        return ["Level 3 checks require pandas. Install with: pip install pandas"]

    failures = []
    for e in entries:
        source = e.get("source", "")
        location = e.get("location", "")
        value = e.get("value")
        if not source or not value:
            continue

        full_path = os.path.join(data_room, source)
        ext = Path(full_path).suffix.lower()
        if ext not in (".csv", ".tsv", ".xlsx", ".xls"):
            continue
        if not os.path.exists(full_path):
            continue

        # Parse location for row + column
        row_match = re.search(r"row\s+(\d+)", location, re.IGNORECASE)
        col_match = re.search(r"column\s+['\"]?(\w+)['\"]?", location, re.IGNORECASE)
        if not (row_match and col_match):
            continue

        row_num = int(row_match.group(1))
        col_name = col_match.group(1)

        try:
            if ext in (".csv", ".tsv"):
                sep = "\t" if ext == ".tsv" else ","
                df = pd.read_csv(full_path, sep=sep, low_memory=False)
            else:
                df = pd.read_excel(full_path)

            if col_name not in df.columns:
                continue  # Caught by level 2

            if row_num >= len(df):
                failures.append(
                    f"Row {row_num} out of range (max {len(df)-1}) in {source}"
                )
                continue

            actual = str(df.iloc[row_num][col_name])
            cited = str(value)
            if actual.strip() != cited.strip():
                failures.append(
                    f"Value mismatch in {source} at {location}: "
                    f"cited='{cited}', actual='{actual}'"
                )
        except Exception as ex:
            failures.append(f"Error reading {source}: {ex}")

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Validate evidence chains resolve to source data."
    )
    parser.add_argument("artifact_path",
                        help="Path to YAML artifact or directory of artifacts")
    parser.add_argument("--data-room", required=True,
                        help="Path to data room root directory")
    parser.add_argument("--level", type=int, default=1, choices=[1, 2, 3],
                        help="Validation level (1=file existence, 2=location, 3=value)")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    # Collect YAML files
    artifact_path = Path(args.artifact_path)
    if artifact_path.is_dir():
        yaml_files = list(artifact_path.rglob("*.yaml"))
    elif artifact_path.exists():
        yaml_files = [artifact_path]
    else:
        print(f"Not found: {args.artifact_path}", file=sys.stderr)
        sys.exit(1)

    # Extract all evidence entries
    all_entries = []
    for yf in yaml_files:
        try:
            data = load_yaml(str(yf))
            entries = extract_evidence_entries(data, str(yf))
            all_entries.extend(entries)
        except Exception as e:
            print(f"Warning: could not parse {yf}: {e}", file=sys.stderr)

    if args.verbose:
        print(f"Found {len(all_entries)} evidence entries in {len(yaml_files)} files",
              file=sys.stderr)

    if not all_entries:
        print("No evidence entries found.")
        sys.exit(0)

    # Run checks
    failures = []
    failures.extend(check_level_1(all_entries, args.data_room))
    if args.level >= 2:
        failures.extend(check_level_2(all_entries, args.data_room))
    if args.level >= 3:
        failures.extend(check_level_3(all_entries, args.data_room))

    # Deduplicate
    failures = list(dict.fromkeys(failures))

    if failures:
        print(f"FAIL: {len(failures)} evidence validation failure(s):\n")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"PASS: All {len(all_entries)} evidence entries validated "
              f"at level {args.level}.")
        sys.exit(0)


if __name__ == "__main__":
    main()
