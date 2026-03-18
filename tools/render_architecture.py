#!/usr/bin/env python3
"""
Render an ETL architecture YAML into a human-readable markdown document.

Produces:
- Pipeline DAG diagram (Mermaid)
- Neo4j schema documentation
- Per-source pipeline specification summary
- Idempotency and incremental strategy
- Simulation integration specification

Usage:
    python tools/render_architecture.py <architecture_path> [--output <path>] [--verbose]
"""

import argparse
import os
import sys
from datetime import datetime

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def render(arch_path: str, verbose: bool) -> str:
    data = load_yaml(arch_path)
    etl = data.get("etl_architecture", data)

    meta = etl.get("metadata", {})
    schema = etl.get("neo4j_schema", {})
    dag = etl.get("pipeline_dag", {})
    specs = etl.get("pipeline_specs", [])
    incremental = etl.get("incremental_strategy", {})
    sim_integration = etl.get("simulation_integration", {})

    lines = []

    # Header
    lines.append(f"# ETL Architecture — {meta.get('company', 'Unknown Company')}")
    lines.append("")
    lines.append(f"Generated from `{arch_path}` on {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"- **Neo4j target:** {meta.get('neo4j_target_version', '?')}")
    lines.append(f"- **Pipeline stages:** {len(dag.get('stages', []))}")
    lines.append(f"- **Source pipelines:** {len(specs)}")
    lines.append("")

    # Pipeline DAG
    stages = dag.get("stages", [])
    if stages:
        lines.append("## Pipeline DAG")
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph TD")
        for stage in stages:
            name = stage.get("name", "?")
            stype = stage.get("type", "")
            entity_types = stage.get("entity_types", [])
            label = f"{name}<br/>{stype}"
            if entity_types:
                label += f"<br/>{', '.join(entity_types)}"
            lines.append(f"    {name}[\"{label}\"]")
            for dep in stage.get("depends_on", []):
                lines.append(f"    {dep} --> {name}")
        lines.append("```")
        lines.append("")

    # Neo4j Schema
    constraints = schema.get("constraints", [])
    indexes = schema.get("indexes", [])

    lines.append("## Neo4j Schema")
    lines.append("")

    if constraints:
        lines.append("### Constraints")
        lines.append("")
        lines.append("| Type | Label | Property |")
        lines.append("|------|-------|----------|")
        for c in constraints:
            lines.append(
                f"| {c.get('type', '')} "
                f"| {c.get('label', '')} "
                f"| `{c.get('property', '')}` |"
            )
        lines.append("")

    if indexes:
        lines.append("### Indexes")
        lines.append("")
        lines.append("| Label | Properties | Type |")
        lines.append("|-------|-----------|------|")
        for idx in indexes:
            props = ", ".join(f"`{p}`" for p in idx.get("properties", []))
            lines.append(
                f"| {idx.get('label', '')} "
                f"| {props} "
                f"| {idx.get('type', '')} |"
            )
        lines.append("")

    # Pipeline Specifications
    if specs:
        lines.append("## Pipeline Specifications")
        lines.append("")

        for spec in specs:
            sid = spec.get("source_id", "?")
            reader = spec.get("reader", {})
            fmt = reader.get("format", "?")
            entities = spec.get("entity_extractions", [])
            rels = spec.get("relationship_extractions", [])
            upsert = spec.get("upsert_strategy", {})
            err = spec.get("error_handling", {})

            lines.append(f"### Source: `{sid}`")
            lines.append("")
            lines.append(f"- **Format:** {fmt}")
            lines.append(f"- **Upsert mode:** {upsert.get('mode', '?')}")
            lines.append(f"- **On error:** {err.get('on_parse_error', '?')}")

            if entities:
                entity_names = [e.get("entity_type", "?") for e in entities]
                lines.append(f"- **Produces entities:** {', '.join(entity_names)}")

            if rels:
                rel_names = [r.get("relationship_type", "?") for r in rels]
                lines.append(f"- **Produces relationships:** {', '.join(rel_names)}")

            preproc = spec.get("preprocessing", [])
            if preproc:
                steps = [f"{s.get('step', '?')}" for s in preproc]
                lines.append(f"- **Preprocessing:** {' → '.join(steps)}")

            lines.append("")

    # Incremental Strategy
    lines.append("## Incremental Strategy")
    lines.append("")
    lines.append(f"- **Detection method:** {incremental.get('detection_method', '?')}")
    ts_fields = incremental.get("timestamp_fields")
    if ts_fields:
        lines.append(f"- **Timestamp fields:** {', '.join(f'`{f}`' for f in ts_fields)}")
    notes = incremental.get("notes")
    if notes:
        lines.append(f"- **Notes:** {notes}")
    lines.append("")

    # Simulation Integration
    lines.append("## Simulation Integration")
    lines.append("")
    lines.append(f"- **Export format:** {sim_integration.get('export_format', '?')}")

    csv_mappings = sim_integration.get("sdg_csv_mapping", [])
    if csv_mappings:
        lines.append("")
        lines.append("### SDG-Compatible CSV Exports")
        lines.append("")
        for cm in csv_mappings:
            lines.append(f"**`{cm.get('simulation_csv', '?')}`**")
            lines.append(f"```cypher")
            lines.append(cm.get("neo4j_query", "// TODO"))
            lines.append(f"```")
            lines.append("")

    profile_queries = sim_integration.get("constraint_profile_queries", [])
    if profile_queries:
        lines.append("### Constraint Profile Queries")
        lines.append("")
        for pq in profile_queries:
            lines.append(f"**`{pq.get('profile_field', '?')}`**")
            lines.append(f"```cypher")
            lines.append(pq.get("neo4j_query", "// TODO"))
            lines.append(f"```")
            lines.append("")

    sim_notes = sim_integration.get("notes")
    if sim_notes:
        lines.append(f"**Notes:** {sim_notes}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Render ETL architecture YAML to human-readable markdown."
    )
    parser.add_argument("architecture_path", help="Path to etl_architecture.yaml")
    parser.add_argument("--output", "-o", help="Output markdown path")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.architecture_path):
        print(f"File not found: {args.architecture_path}", file=sys.stderr)
        sys.exit(1)

    doc = render(args.architecture_path, args.verbose)

    if args.output:
        with open(args.output, "w") as f:
            f.write(doc)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
