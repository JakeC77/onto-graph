# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Builder Test Data Generator
============================
Generates 2 years of realistic operational data for a $1M-$3M trade builder.

Usage:
    python generate.py                          # default: 2024-01-01 to 2025-12-31
    python generate.py --seed 42                # reproducible output
    python generate.py --start 2024-01-01 --end 2025-12-31
    python generate.py --format json            # default
    python generate.py --format csv             # one file per entity type
    python generate.py --format sqlite          # single .db file
    python generate.py --out ./output           # output directory
    python generate.py --summary                # print stats after generation
"""

import argparse
import json
import os
import random
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent))

from generators.base import Registry
from generators.company import load_config, seed_master_data
from generators.narrative import apply_narrative_events, generate_narrative_time_entries
from generators.projects import generate_project_pipeline
from generators.execution import generate_execution
from generators.financials import generate_invoices, generate_overhead_bills


#  Helpers 

def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


#  Output writers 

def write_json(registry: Registry, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    data = registry.to_dict()
    out_path = out_dir / "data.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, default=json_default)
    print(f"  Wrote {out_path}")


def write_csv(registry: Registry, out_dir: Path) -> None:
    import csv
    out_dir.mkdir(parents=True, exist_ok=True)
    data = registry.to_dict()
    for entity_type, records in data.items():
        if not records:
            continue
        out_path = out_dir / f"{entity_type}.csv"
        # Union of all field names across all records (handles dynamic fields)
        fieldnames = list(dict.fromkeys(k for r in records for k in r.keys()))
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
        print(f"  Wrote {out_path} ({len(records)} rows)")


def write_sqlite(registry: Registry, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / "builder.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    data = registry.to_dict()

    for entity_type, records in data.items():
        if not records:
            continue

        # Infer schema from first record
        columns = list(records[0].keys())
        col_defs = []
        for col in columns:
            # Simple type inference
            sample = next((r[col] for r in records if r.get(col) is not None), None)
            if isinstance(sample, bool):
                col_defs.append(f'"{col}" INTEGER')
            elif isinstance(sample, int):
                col_defs.append(f'"{col}" INTEGER')
            elif isinstance(sample, float):
                col_defs.append(f'"{col}" REAL')
            elif isinstance(sample, list):
                col_defs.append(f'"{col}" TEXT')  # JSON-encoded
            else:
                col_defs.append(f'"{col}" TEXT')

        ddl = f'CREATE TABLE IF NOT EXISTS "{entity_type}" ({", ".join(col_defs)})'
        conn.execute(ddl)

        for record in records:
            row = {}
            for col in columns:
                val = record.get(col)
                if isinstance(val, list):
                    val = json.dumps(val)
                elif isinstance(val, bool):
                    val = int(val)
                row[col] = val

            placeholders = ", ".join(["?"] * len(columns))
            col_list = ", ".join(f'"{c}"' for c in columns)
            conn.execute(
                f'INSERT INTO "{entity_type}" ({col_list}) VALUES ({placeholders})',
                [row[c] for c in columns]
            )

    conn.commit()
    conn.close()
    print(f"  Wrote {db_path}")


#  Summary 

def print_summary(registry: Registry) -> None:
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    data = registry.to_dict()
    counts = {k: len(v) for k, v in data.items()}

    # Entity counts
    print("\nEntity counts:")
    for entity, count in sorted(counts.items()):
        print(f"  {entity:<28} {count:>6}")

    # Financial totals
    print("\nFinancial totals:")
    invoices = registry.all("invoice")
    total_billed = sum(i.get("total_due", 0) for i in invoices if i.get("type") != "retention")
    total_retention = sum(i.get("retention_held", 0) for i in invoices)
    payments = registry.all("payment")
    total_received = sum(p.get("amount", 0) for p in payments)
    bills = registry.all("bill")
    project_bills = [b for b in bills if b.get("project_id")]
    overhead_bills = [b for b in bills if not b.get("project_id")]
    total_project_cost = sum(b.get("total", 0) for b in project_bills)
    total_overhead = sum(b.get("total", 0) for b in overhead_bills)

    time_entries = registry.all("time_entry")
    total_labor_cost = sum(t.get("cost", 0) for t in time_entries)
    total_hours = sum(t.get("hours_regular", 0) + t.get("hours_overtime", 0) for t in time_entries)

    print(f"  Total billed (ex. retention) ${total_billed:>14,.2f}")
    print(f"  Total retention held         ${total_retention:>14,.2f}")
    print(f"  Total payments received      ${total_received:>14,.2f}")
    print(f"  Total project costs (bills)  ${total_project_cost:>14,.2f}")
    print(f"  Total labor cost             ${total_labor_cost:>14,.2f}")
    print(f"  Total labor hours            {total_hours:>15,.1f}")
    print(f"  Total overhead               ${total_overhead:>14,.2f}")

    # Project breakdown
    print("\nProject breakdown:")
    projects = registry.all("project")
    won = [p for p in projects if p["status"] != "lost"]
    by_type: dict[str, list] = {}
    for p in won:
        by_type.setdefault(p["type"], []).append(p)
    for ptype, ps in sorted(by_type.items()):
        total_cv = sum(p.get("contract_amount", 0) for p in ps)
        print(f"  {ptype:<24} {len(ps):>3} projects  ${total_cv:>12,.0f} contract value")

    estimates = registry.all("estimate")
    won_ests = [e for e in estimates if e["status"] == "accepted"]
    print(f"\n  Win rate: {len(won_ests)}/{len(estimates)} = {len(won_ests)/max(1,len(estimates))*100:.1f}%")

    print("=" * 60)


#  Main 

def main():
    parser = argparse.ArgumentParser(description="Generate builder test data")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--start", type=str, default="2024-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2025-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--format", choices=["json", "csv", "sqlite", "all"], default="all",
                        help="Output format")
    parser.add_argument("--out", type=str, default="./output", help="Output directory")
    parser.add_argument("--config", type=str, default="./config", help="Config directory")
    parser.add_argument("--summary", action="store_true", default=True,
                        help="Print summary after generation")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(1, 999999)
    print(f"\nBuilder Test Data Generator")
    print(f"  Seed:   {seed}  (pass --seed {seed} to reproduce)")
    print(f"  Period: {args.start} to {args.end}")
    print(f"  Format: {args.format}")
    print(f"  Output: {args.out}\n")

    rng = random.Random(seed)
    start_date = parse_date(args.start)
    end_date = parse_date(args.end)

    #  Load config 
    print("Loading config...")
    raw = load_config(args.config)
    # Normalized cfg  flat structure, each key is the parsed content
    cfg = {
        "company": raw["company"],          # full company.yaml dict
        "archetypes": raw["archetypes"]["archetypes"],  # archetype defs only
        "customers": raw["archetypes"].get("customers", {}),
        "events": raw["events"],            # full events.yaml dict
    }
    # Convenience aliases matching what generators expect
    cfg["financials"] = cfg["company"]["financials"]
    cfg["win_rate_by_type"] = cfg["company"].get("win_rate_by_type", {})
    cfg["crew_timeline"] = cfg["company"].get("crew_timeline", [])
    cfg["vendors"] = cfg["company"].get("vendors", [])

    #  Registry 
    registry = Registry()

    #  Seed master data 
    print("Seeding master data (company, vendors, customers, crew)...")
    seed_master_data(cfg, registry)

    #  Apply narrative events (crew changes, pricing, etc.) 
    print("Applying narrative events...")
    events_by_tag = apply_narrative_events(cfg, registry)

    #  Generate project pipeline 
    print("Generating project pipeline (estimates + projects + jobs)...")
    narrative_tags = {tag: evts for tag, evts in events_by_tag.items()}
    generate_project_pipeline(
        cfg=cfg,
        registry=registry,
        start_date=start_date,
        end_date=end_date,
        rng=rng,
        narrative_tags=narrative_tags,
    )

    #  Generate execution (time entries, bills, COs) 
    print("Generating execution layer (time entries, material bills, sub bills)...")
    generate_execution(
        cfg=cfg,
        registry=registry,
        rng=rng,
        events_by_tag=events_by_tag,
    )

    #  Narrative-driven time entries (overtime spikes, etc.) 
    print("Injecting narrative time entries (OT events, etc.)...")
    generate_narrative_time_entries(cfg, registry, rng)

    #  Generate invoices and payments 
    print("Generating invoices and payments...")
    generate_invoices(
        cfg=cfg,
        registry=registry,
        rng=rng,
        events_by_tag=events_by_tag,
    )

    #  Generate overhead bills 
    print("Generating overhead bills...")
    generate_overhead_bills(
        cfg=cfg,
        registry=registry,
        rng=rng,
        start_date=start_date,
        end_date=end_date,
    )

    #  Write output 
    out_dir = Path(args.out)
    print(f"\nWriting output to {out_dir}/")

    fmt = args.format
    if fmt in ("json", "all"):
        write_json(registry, out_dir)
    if fmt in ("csv", "all"):
        write_csv(registry, out_dir / "csv")
    if fmt in ("sqlite", "all"):
        write_sqlite(registry, out_dir)

    #  Summary 
    if args.summary:
        print_summary(registry)

    print(f"\nDone. Seed was {seed}.")


if __name__ == "__main__":
    main()
