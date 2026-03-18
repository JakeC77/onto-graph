#!/usr/bin/env python3
"""
Profile a tabular data source (CSV, Excel, TSV).

Produces a YAML statistical profile with column-level details:
type inference, cardinality, null rates, uniqueness, sample values,
candidate key/FK detection, grain estimation, and date range.

Usage:
    python tools/profile_source.py <file_path> [--sheet <name>] [--output <path>] [--verbose]
    python tools/profile_source.py <file_path> --all-sheets [--output-dir <dir>] [--verbose]

Examples:
    python tools/profile_source.py ~/DataRoom/employees.csv
    python tools/profile_source.py ~/DataRoom/financials.xlsx --sheet "Q3 Actuals"
    python tools/profile_source.py ~/DataRoom/financials.xlsx --all-sheets --output-dir ./profiles/
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas openpyxl", file=sys.stderr)
    sys.exit(1)


def infer_column_type(series: "pd.Series") -> str:
    """Infer the semantic type of a column from its values."""
    if series.dropna().empty:
        return "unknown"

    # Try numeric
    numeric = pd.to_numeric(series.dropna(), errors="coerce")
    if numeric.notna().sum() / max(series.dropna().shape[0], 1) > 0.9:
        if (numeric.dropna() == numeric.dropna().astype(int)).all():
            return "integer"
        return "float"

    # Try date
    try:
        dates = pd.to_datetime(series.dropna(), errors="coerce", infer_datetime_format=True)
        if dates.notna().sum() / max(series.dropna().shape[0], 1) > 0.8:
            return "date"
    except Exception:
        pass

    # Try boolean
    bool_values = {"true", "false", "yes", "no", "y", "n", "1", "0", "t", "f"}
    if series.dropna().astype(str).str.lower().isin(bool_values).mean() > 0.9:
        return "boolean"

    # Check if it looks like an ID
    str_vals = series.dropna().astype(str)
    if series.nunique() / max(series.shape[0], 1) > 0.9:
        # High cardinality string — likely an ID
        return "id"

    return "string"


def detect_grain(df: "pd.DataFrame", columns: list[dict]) -> str | None:
    """Attempt to detect what one row represents."""
    # Look for columns that are unique (candidate keys)
    candidate_keys = [c["name"] for c in columns if c["is_candidate_key"]]
    if candidate_keys:
        # The candidate key often names the grain
        key = candidate_keys[0]
        key_lower = key.lower()
        # Common patterns
        for entity, keywords in [
            ("one employee", ["emp", "employee", "person", "staff", "worker"]),
            ("one customer", ["cust", "customer", "client", "account"]),
            ("one contract", ["contract", "agreement", "deal"]),
            ("one transaction", ["trans", "txn", "transaction", "payment"]),
            ("one department", ["dept", "department", "division", "team"]),
            ("one invoice", ["invoice", "bill"]),
            ("one order", ["order", "po", "purchase"]),
            ("one initiative", ["initiative", "project", "program"]),
        ]:
            if any(kw in key_lower for kw in keywords):
                return entity
        return f"one record per unique {key}"
    return None


def profile_dataframe(
    df: "pd.DataFrame", file_path: str, sheet_name: str | None = None
) -> dict:
    """Profile a single DataFrame and return the profile dict."""
    # Use slugified filename as source_id (readable, stable, unique per file)
    stem = Path(file_path).stem.lower()
    # Replace non-alphanumeric chars with underscores, collapse runs
    slug = "".join(c if c.isalnum() or c == "_" else "_" for c in stem)
    slug = "_".join(part for part in slug.split("_") if part)
    if sheet_name:
        sheet_slug = "".join(c if c.isalnum() or c == "_" else "_" for c in sheet_name.lower())
        sheet_slug = "_".join(part for part in sheet_slug.split("_") if part)
        slug = f"{slug}__{sheet_slug}"
    source_id = slug

    columns = []
    for col in df.columns:
        series = df[col]
        col_type = infer_column_type(series)
        cardinality = int(series.nunique())
        null_rate = round(float(series.isna().mean()), 4)
        is_unique = cardinality == len(series) and null_rate == 0
        is_candidate_key = is_unique and cardinality > 1

        # Sample values (up to 10 non-null unique values)
        samples = series.dropna().unique()[:10].tolist()
        samples = [str(s) for s in samples]

        # Candidate FK: non-unique ID-like column
        is_candidate_fk = (
            col_type in ("id", "integer", "string")
            and not is_candidate_key
            and cardinality > 1
            and cardinality < len(series) * 0.9
            and any(
                kw in col.lower()
                for kw in ["id", "code", "key", "ref", "num", "number"]
            )
        )

        columns.append({
            "name": col,
            "inferred_type": col_type,
            "null_rate": null_rate,
            "cardinality": cardinality,
            "is_unique": is_unique,
            "sample_values": samples,
            "is_candidate_key": is_candidate_key,
            "is_candidate_fk": is_candidate_fk,
        })

    # Detect date range
    date_cols = [c for c in columns if c["inferred_type"] == "date"]
    date_range = {"earliest": None, "latest": None}
    if date_cols:
        for dc in date_cols:
            try:
                dates = pd.to_datetime(df[dc["name"]], errors="coerce").dropna()
                if not dates.empty:
                    earliest = dates.min().isoformat()[:10]
                    latest = dates.max().isoformat()[:10]
                    if date_range["earliest"] is None or earliest < date_range["earliest"]:
                        date_range["earliest"] = earliest
                    if date_range["latest"] is None or latest > date_range["latest"]:
                        date_range["latest"] = latest
            except Exception:
                pass

    grain = detect_grain(df, columns)

    profile = {
        "source_id": source_id,
        "path": file_path,
        "format": Path(file_path).suffix.lstrip(".").lower(),
        "size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        "sheet_name": sheet_name,
        "columns": columns,
        "row_count": len(df),
        "grain": grain,
        "date_range": date_range,
    }

    return profile


def profile_file(file_path: str, sheet_name: str | None = None) -> list[dict]:
    """Profile a file and return list of profiles (one per sheet for Excel)."""
    ext = Path(file_path).suffix.lower()
    profiles = []

    if ext in (".csv", ".tsv"):
        sep = "\t" if ext == ".tsv" else ","
        try:
            df = pd.read_csv(file_path, sep=sep, low_memory=False)
        except Exception as e:
            # Try with different encoding
            try:
                df = pd.read_csv(file_path, sep=sep, encoding="latin-1", low_memory=False)
            except Exception:
                print(f"Error reading {file_path}: {e}", file=sys.stderr)
                return []
        profiles.append(profile_dataframe(df, file_path))

    elif ext in (".xlsx", ".xls", ".xlsm"):
        try:
            xls = pd.ExcelFile(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return []

        sheets = [sheet_name] if sheet_name else xls.sheet_names
        for sn in sheets:
            try:
                df = pd.read_excel(xls, sheet_name=sn)
                profiles.append(profile_dataframe(df, file_path, sheet_name=sn))
            except Exception as e:
                print(f"Error reading sheet '{sn}' in {file_path}: {e}", file=sys.stderr)

    else:
        print(f"Unsupported format: {ext} ({file_path})", file=sys.stderr)

    return profiles


def main():
    parser = argparse.ArgumentParser(
        description="Profile a tabular data source."
    )
    parser.add_argument("file_path", help="Path to CSV or Excel file")
    parser.add_argument("--sheet", help="Sheet name (Excel only)")
    parser.add_argument("--all-sheets", action="store_true",
                        help="Profile all sheets (Excel only)")
    parser.add_argument("--output", "-o", help="Output YAML path (single file)")
    parser.add_argument("--output-dir", help="Output directory (one file per profile)")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()
    file_path = os.path.abspath(args.file_path)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Profiling: {file_path}", file=sys.stderr)

    profiles = profile_file(file_path, sheet_name=args.sheet)

    if not profiles:
        print("No profiles generated.", file=sys.stderr)
        sys.exit(1)

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        for p in profiles:
            name = Path(file_path).stem
            if p.get("sheet_name"):
                name += f"_{p['sheet_name']}"
            out_path = os.path.join(args.output_dir, f"{name}_profile.yaml")
            with open(out_path, "w") as f:
                yaml.dump(p, f, default_flow_style=False, sort_keys=False)
            if args.verbose:
                print(f"Wrote: {out_path}", file=sys.stderr)
    elif args.output:
        with open(args.output, "w") as f:
            yaml.dump(profiles if len(profiles) > 1 else profiles[0],
                       f, default_flow_style=False, sort_keys=False)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(yaml.dump(profiles if len(profiles) > 1 else profiles[0],
                         default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
