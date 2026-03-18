#!/usr/bin/env python3
"""
Validate a data catalog for completeness and conformance.

Checks:
1. Every file in the data room is listed in the catalog
2. Every tabular source has a statistical profile
3. Catalog YAML conforms to the schema structure
4. Join candidates reference valid source IDs
5. Gaps have severity and downstream impact

Usage:
    python tools/validate_catalog.py <catalog_path> --data-room <path> [--profiles-dir <path>] [--verbose]

Exit codes:
    0 = all checks pass
    1 = validation failures found
"""

import argparse
import os
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_data_room_files(data_room_path: str) -> set[str]:
    """Get all file paths relative to data room root."""
    files = set()
    root = Path(data_room_path)
    for f in root.rglob("*"):
        if f.is_file():
            files.add(str(f.relative_to(root)).replace("\\", "/"))
    return files


def validate(catalog_path: str, data_room_path: str,
             profiles_dir: str | None, verbose: bool) -> list[str]:
    """Run all validation checks. Returns list of failure messages."""
    failures = []

    # Load catalog
    try:
        catalog = load_yaml(catalog_path)
    except Exception as e:
        return [f"Cannot parse catalog YAML: {e}"]

    data_catalog = catalog.get("data_catalog", catalog)

    # Check 1: Required top-level sections
    required_sections = ["metadata", "sources", "join_candidates",
                         "candidate_entity_types", "gaps"]
    for section in required_sections:
        if section not in data_catalog:
            failures.append(f"Missing required section: {section}")

    sources = data_catalog.get("sources", [])
    source_ids = {s.get("source_id") for s in sources}
    catalog_paths = {s.get("path") for s in sources}

    # Check 2: Every file in data room is in catalog
    if data_room_path and os.path.isdir(data_room_path):
        actual_files = get_data_room_files(data_room_path)
        missing = actual_files - catalog_paths
        for f in sorted(missing):
            failures.append(f"File not in catalog: {f}")
        if verbose and not missing:
            print(f"  OK: All {len(actual_files)} files cataloged", file=sys.stderr)

    # Check 3: Every tabular source has a profile
    tabular_formats = {"csv", "xlsx", "xls", "xlsm", "tsv"}
    tabular_sources = [s for s in sources
                       if s.get("format", "").lower() in tabular_formats]

    if profiles_dir and os.path.isdir(profiles_dir):
        profile_files = set(Path(profiles_dir).glob("*.yaml"))
        profiled_ids = set()
        for pf in profile_files:
            try:
                p = load_yaml(str(pf))
                if isinstance(p, dict) and "source_id" in p:
                    profiled_ids.add(p["source_id"])
            except Exception:
                pass

        for s in tabular_sources:
            sid = s.get("source_id")
            if sid and sid not in profiled_ids:
                failures.append(f"Tabular source missing profile: {s.get('path')} ({sid})")

        if verbose and not any("missing profile" in f for f in failures):
            print(f"  OK: All {len(tabular_sources)} tabular sources profiled",
                  file=sys.stderr)

    # Check 4: Source structure
    for i, s in enumerate(sources):
        if not s.get("source_id"):
            failures.append(f"Source {i} missing source_id")
        if not s.get("path"):
            failures.append(f"Source {i} missing path")
        if not s.get("format"):
            failures.append(f"Source {i} missing format")

    # Check 5: Join candidates reference valid source IDs
    joins = data_catalog.get("join_candidates", [])
    for j in joins:
        if j.get("source_a") and j["source_a"] not in source_ids:
            failures.append(f"Join references unknown source_a: {j['source_a']}")
        if j.get("source_b") and j["source_b"] not in source_ids:
            failures.append(f"Join references unknown source_b: {j['source_b']}")

    # Check 6: Gaps have required fields
    gaps = data_catalog.get("gaps", [])
    for i, g in enumerate(gaps):
        if not g.get("description"):
            failures.append(f"Gap {i} missing description")
        if not g.get("severity"):
            failures.append(f"Gap {i} missing severity")
        if g.get("severity") and g["severity"] not in ("critical", "significant", "minor"):
            failures.append(f"Gap {i} invalid severity: {g['severity']}")
        if not g.get("downstream_impact"):
            failures.append(f"Gap {i} missing downstream_impact")

    # Check 7: Candidate entity types
    candidates = data_catalog.get("candidate_entity_types", [])
    if not candidates:
        failures.append("No candidate entity types identified")
    for c in candidates:
        if not c.get("name"):
            failures.append("Candidate entity type missing name")
        if not c.get("sources"):
            failures.append(f"Candidate entity type '{c.get('name')}' has no sources")

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Validate a data catalog for completeness."
    )
    parser.add_argument("catalog_path", help="Path to data_catalog.yaml")
    parser.add_argument("--data-room", help="Path to raw data room directory")
    parser.add_argument("--profiles-dir", help="Path to source_profiles/ directory")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.catalog_path):
        print(f"File not found: {args.catalog_path}", file=sys.stderr)
        sys.exit(1)

    failures = validate(
        args.catalog_path,
        args.data_room,
        args.profiles_dir,
        args.verbose,
    )

    if failures:
        print(f"FAIL: {len(failures)} validation failure(s):\n")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("PASS: All catalog validation checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
