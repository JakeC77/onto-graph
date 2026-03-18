#!/usr/bin/env python3
"""
Detect potential join keys across profiled data sources.

Reads source profiles (from profile_source.py) and finds columns across
different sources that share values, indicating potential join relationships.

Usage:
    python tools/detect_joins.py <profiles_dir> [--output <path>] [--min-overlap 0.3] [--verbose]

Examples:
    python tools/detect_joins.py runs/acme_20260317/phase_0_catalog/source_profiles/
    python tools/detect_joins.py ./profiles/ --min-overlap 0.5 --output joins.yaml
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas", file=sys.stderr)
    sys.exit(1)


def load_profiles(profiles_dir: str) -> list[dict]:
    """Load all YAML profiles from a directory."""
    profiles = []
    for f in sorted(Path(profiles_dir).glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                if isinstance(data, list):
                    profiles.extend(data)
                else:
                    profiles.append(data)
    return profiles


def load_source_data(profile: dict) -> "pd.DataFrame | None":
    """Load the actual data for a profiled source."""
    path = profile["path"]
    ext = Path(path).suffix.lower()

    try:
        if ext in (".csv", ".tsv"):
            sep = "\t" if ext == ".tsv" else ","
            try:
                return pd.read_csv(path, sep=sep, low_memory=False)
            except Exception:
                return pd.read_csv(path, sep=sep, encoding="latin-1", low_memory=False)
        elif ext in (".xlsx", ".xls", ".xlsm"):
            sheet = profile.get("sheet_name")
            return pd.read_excel(path, sheet_name=sheet)
    except Exception as e:
        print(f"Warning: could not load {path}: {e}", file=sys.stderr)

    return None


def compute_overlap(values_a: set, values_b: set) -> float:
    """Compute the fraction of values in A that appear in B."""
    if not values_a:
        return 0.0
    return len(values_a & values_b) / len(values_a)


def detect_joins(
    profiles: list[dict],
    min_overlap: float = 0.3,
    verbose: bool = False,
) -> list[dict]:
    """Find join-key candidates across all profile pairs."""

    # Load actual data for all profiles
    source_data = {}
    for p in profiles:
        key = (p["path"], p.get("sheet_name"))
        df = load_source_data(p)
        if df is not None:
            source_data[key] = df

    # Get candidate columns (keys and FKs) per source
    source_candidates = {}
    for p in profiles:
        key = (p["path"], p.get("sheet_name"))
        if key not in source_data:
            continue
        candidates = []
        for col in p.get("columns", []):
            if col.get("is_candidate_key") or col.get("is_candidate_fk"):
                candidates.append(col["name"])
            # Also include ID-typed columns
            elif col.get("inferred_type") == "id":
                candidates.append(col["name"])
        source_candidates[key] = {
            "profile": p,
            "candidates": candidates,
        }

    # Compare all pairs
    joins = []
    keys = list(source_candidates.keys())

    for i, key_a in enumerate(keys):
        for key_b in keys[i + 1:]:
            info_a = source_candidates[key_a]
            info_b = source_candidates[key_b]
            df_a = source_data[key_a]
            df_b = source_data[key_b]

            for col_a in info_a["candidates"]:
                if col_a not in df_a.columns:
                    continue
                values_a = set(df_a[col_a].dropna().astype(str))
                if not values_a:
                    continue

                for col_b in info_b["candidates"]:
                    if col_b not in df_b.columns:
                        continue
                    values_b = set(df_b[col_b].dropna().astype(str))
                    if not values_b:
                        continue

                    overlap_ab = compute_overlap(values_a, values_b)
                    overlap_ba = compute_overlap(values_b, values_a)
                    max_overlap = max(overlap_ab, overlap_ba)

                    if max_overlap >= min_overlap:
                        # Confidence: high overlap in both directions = high confidence
                        confidence = round(min(overlap_ab, overlap_ba) * 0.7
                                           + max_overlap * 0.3, 3)

                        join = {
                            "source_a": info_a["profile"]["source_id"],
                            "column_a": col_a,
                            "source_b": info_b["profile"]["source_id"],
                            "column_b": col_b,
                            "overlap_rate": round(max_overlap, 3),
                            "confidence": confidence,
                            "notes": f"A→B: {overlap_ab:.1%}, B→A: {overlap_ba:.1%}",
                        }
                        joins.append(join)

                        if verbose:
                            print(
                                f"  {col_a} ({info_a['profile']['path']}) ↔ "
                                f"{col_b} ({info_b['profile']['path']}): "
                                f"overlap={max_overlap:.1%}, confidence={confidence}",
                                file=sys.stderr,
                            )

    # Sort by confidence descending
    joins.sort(key=lambda j: j["confidence"], reverse=True)
    return joins


def main():
    parser = argparse.ArgumentParser(
        description="Detect join-key candidates across profiled sources."
    )
    parser.add_argument("profiles_dir", help="Directory of source profile YAMLs")
    parser.add_argument("--output", "-o", help="Output YAML path")
    parser.add_argument("--min-overlap", type=float, default=0.3,
                        help="Minimum overlap rate to report (default: 0.3)")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.isdir(args.profiles_dir):
        print(f"Not a directory: {args.profiles_dir}", file=sys.stderr)
        sys.exit(1)

    profiles = load_profiles(args.profiles_dir)
    if not profiles:
        print("No profiles found.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Loaded {len(profiles)} profiles. Detecting joins...", file=sys.stderr)

    joins = detect_joins(profiles, min_overlap=args.min_overlap, verbose=args.verbose)

    output = {
        "join_candidates": joins,
        "total_candidates": len(joins),
        "profiles_analyzed": len(profiles),
    }

    if args.output:
        with open(args.output, "w") as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False)
        if args.verbose:
            print(f"Wrote {len(joins)} candidates to {args.output}", file=sys.stderr)
    else:
        print(yaml.dump(output, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
