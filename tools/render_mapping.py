#!/usr/bin/env python3
"""
Render a mapping plan YAML into a human-readable markdown document.

Produces:
- Source-to-entity mapping tables
- Field-level mapping detail
- Gap inventory
- Statistical computation specifications
- Source utilization summary

Usage:
    python tools/render_mapping.py <mapping_path> [--output <path>] [--verbose]
"""

import argparse
import os
import sys
from datetime import datetime

import yaml


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def render(mapping_path: str, verbose: bool) -> str:
    data = load_yaml(mapping_path)
    mp = data.get("mapping_plan", data)

    meta = mp.get("metadata", {})
    entity_mappings = mp.get("entity_mappings", [])
    relationship_mappings = mp.get("relationship_mappings", [])
    stat_computations = mp.get("statistical_computations", [])
    coverage = mp.get("coverage", {})
    source_util = mp.get("source_utilization", [])

    lines = []

    # Header
    lines.append(f"# Data Mapping Plan — {meta.get('company', 'Unknown Company')}")
    lines.append("")
    lines.append(f"Generated from `{mapping_path}` on {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    # Coverage summary
    cov_rate = coverage.get("coverage_rate", 0)
    lines.append("## Coverage Summary")
    lines.append("")
    lines.append(f"- **Properties mapped:** {coverage.get('properties_mapped', '?')}")
    lines.append(f"- **Properties gapped:** {coverage.get('properties_gapped', '?')}")
    lines.append(f"- **Coverage rate:** {cov_rate:.0%}" if isinstance(cov_rate, (int, float)) else f"- **Coverage rate:** {cov_rate}")
    lines.append(f"- **Entity mappings:** {len(entity_mappings)}")
    lines.append(f"- **Relationship mappings:** {len(relationship_mappings)}")
    lines.append(f"- **Statistical computations:** {len(stat_computations)}")
    lines.append("")

    # Entity Mappings
    lines.append("## Entity Mappings")
    lines.append("")

    for em in entity_mappings:
        et = em.get("entity_type", "Unknown")
        sor = em.get("system_of_record", "?")
        merge_key = em.get("merge_key", "?")
        conflict = em.get("conflict_resolution", "?")
        additional = em.get("additional_sources", [])

        lines.append(f"### {et}")
        lines.append("")
        lines.append(f"- **System of record:** `{sor}`")
        lines.append(f"- **Merge key:** `{merge_key}`")
        lines.append(f"- **Conflict resolution:** {conflict}")
        if additional:
            lines.append(f"- **Additional sources:** {', '.join(f'`{s}`' for s in additional)}")
        lines.append("")

        field_mappings = em.get("field_mappings", [])
        if field_mappings:
            lines.append("| Target Property | Source | Source Field | Transform | Null Handling |")
            lines.append("|----------------|--------|-------------|-----------|---------------|")
            for fm in field_mappings:
                lines.append(
                    f"| `{fm.get('target_property', '')}` "
                    f"| `{fm.get('source', '')}` "
                    f"| `{fm.get('source_field', '')}` "
                    f"| {fm.get('transformation', 'none')} "
                    f"| {fm.get('null_handling', 'skip')} |"
                )
            lines.append("")

    # Relationship Mappings
    if relationship_mappings:
        lines.append("## Relationship Mappings")
        lines.append("")
        lines.append("| Relationship | Method | Source | From Field | To Field | Confidence |")
        lines.append("|-------------|--------|--------|------------|----------|-----------|")
        for rm in relationship_mappings:
            lines.append(
                f"| `{rm.get('relationship_type', '')}` "
                f"| {rm.get('extraction_method', '')} "
                f"| `{rm.get('source', '')}` "
                f"| `{rm.get('from_field', '')}` "
                f"| `{rm.get('to_field', '')}` "
                f"| {rm.get('confidence', '')} |"
            )
        lines.append("")

    # Statistical Computations
    if stat_computations:
        lines.append("## Statistical Computations")
        lines.append("")
        for sc in stat_computations:
            lines.append(f"### {sc.get('name', 'Unknown')}")
            lines.append("")
            lines.append(f"**Target:** `{sc.get('target_entity_type', '')}.{sc.get('target_property', '')}`")
            lines.append(f"**Formula:** `{sc.get('formula', '')}`")
            lines.append(f"**Output type:** {sc.get('output_type', '')}")
            lines.append("")
            inputs = sc.get("inputs", [])
            if inputs:
                lines.append("**Inputs:**")
                for inp in inputs:
                    window = f" (window: {inp['window']})" if inp.get("window") else ""
                    lines.append(
                        f"- `{inp.get('source', '')}.{inp.get('field', '')}` "
                        f"→ {inp.get('aggregation', 'raw')}{window}"
                    )
                lines.append("")

    # Gaps
    gaps = coverage.get("gaps", [])
    if gaps:
        lines.append("## Gaps")
        lines.append("")
        lines.append("| Entity Type | Property | Reason | Downstream Impact |")
        lines.append("|------------|----------|--------|-------------------|")
        for g in gaps:
            lines.append(
                f"| {g.get('entity_type', '')} "
                f"| `{g.get('property', '')}` "
                f"| {g.get('reason', '')} "
                f"| {g.get('downstream_impact', '')} |"
            )
        lines.append("")

    # Source Utilization
    if source_util:
        lines.append("## Source Utilization")
        lines.append("")
        consumed = [s for s in source_util if s.get("consumed")]
        excluded = [s for s in source_util if not s.get("consumed")]

        lines.append(f"**Consumed:** {len(consumed)} sources | **Excluded:** {len(excluded)} sources")
        lines.append("")

        if excluded:
            lines.append("### Excluded Sources")
            lines.append("")
            for s in excluded:
                lines.append(f"- `{s.get('source_id', '')}`: {s.get('exclusion_reason', 'no reason given')}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Render mapping plan YAML to human-readable markdown."
    )
    parser.add_argument("mapping_path", help="Path to mapping_plan.yaml")
    parser.add_argument("--output", "-o", help="Output markdown path")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.mapping_path):
        print(f"File not found: {args.mapping_path}", file=sys.stderr)
        sys.exit(1)

    doc = render(args.mapping_path, args.verbose)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(doc)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
