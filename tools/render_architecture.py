#!/usr/bin/env python3
"""
Render an ETL architecture YAML into a PRD-style markdown document.

Produces a document an engineer can build from: pipeline DAG, Neo4j schema
with Cypher, per-source pipeline specs with preprocessing detail, relationship
extraction expressions, upsert strategies, and error handling.

Usage:
    python tools/render_architecture.py <architecture_path> [--output <path>] [--verbose]
"""

import argparse
import os
import re
import sys
from datetime import datetime

import yaml


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def source_label(source_id: str) -> str:
    """Turn a source_id into a human-readable label."""
    if re.match(r"^[a-z][a-z0-9_]+$", source_id) and len(source_id) > 3:
        return f"{source_id}.csv"
    return source_id


def render(arch_path: str, verbose: bool) -> str:
    data = load_yaml(arch_path)
    etl = data.get("etl_architecture", data)

    meta = etl.get("metadata", {})
    schema = etl.get("neo4j_schema", {})
    dag = etl.get("pipeline_dag", {})
    specs = etl.get("pipeline_specs", [])
    incremental = etl.get("incremental_strategy", {})
    sim_integration = etl.get("simulation_integration", {})

    company = meta.get("company", "Unknown Company")
    lines = []

    # ── Overview ──────────────────────────────────────────────────────────
    lines.append(f"# ETL Pipeline Specification — {company}")
    lines.append("")
    lines.append(f"Generated from `{arch_path}` on {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    stages = dag.get("stages", [])
    all_entity_types = set()
    all_rel_types = set()
    for spec in specs:
        for ee in spec.get("entity_extractions", []):
            all_entity_types.add(ee.get("entity_type", ""))
        for re_ in spec.get("relationship_extractions", []):
            all_rel_types.add(re_.get("relationship_type", ""))
    total_rows = sum(s.get("estimated_rows", 0) for s in stages)

    lines.append("## Overview")
    lines.append("")
    lines.append("| Attribute | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| **Company** | {company} |")
    lines.append(f"| **Neo4j target** | {meta.get('neo4j_target_version', '?')} |")
    lines.append(f"| **Pipeline stages** | {len(stages)} |")
    lines.append(f"| **Source pipelines** | {len(specs)} |")
    lines.append(f"| **Entity types loaded** | {len(all_entity_types)} |")
    lines.append(f"| **Relationship types created** | {len(all_rel_types)} |")
    lines.append(f"| **Estimated total rows** | {total_rows:,} |")
    lines.append(f"| **Mapping plan** | `{meta.get('mapping_plan_ref', '—')}` |")
    lines.append("")
    lines.append(
        f"This pipeline reads {len(specs)} CSV source files, transforms and loads "
        f"them into a Neo4j {meta.get('neo4j_target_version', '5.x')} graph database "
        f"containing {len(all_entity_types)} node types and {len(all_rel_types)} "
        f"relationship types. All loads use idempotent MERGE operations."
    )
    lines.append("")

    # ── Pipeline DAG ──────────────────────────────────────────────────────
    if stages:
        lines.append("## Pipeline Execution Order")
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

        lines.append("| Stage | Type | Depends On | Entity Types | Est. Rows |")
        lines.append("|-------|------|-----------|--------------|-----------|")
        for stage in stages:
            name = stage.get("name", "?")
            stype = stage.get("type", "")
            deps = ", ".join(stage.get("depends_on", [])) or "—"
            etypes = ", ".join(stage.get("entity_types", [])) or "—"
            rows = stage.get("estimated_rows", "—")
            if isinstance(rows, int):
                rows = f"{rows:,}"
            lines.append(f"| {name} | {stype} | {deps} | {etypes} | {rows} |")
        lines.append("")

    # ── Neo4j Schema ──────────────────────────────────────────────────────
    constraints = schema.get("constraints", [])
    indexes = schema.get("indexes", [])

    lines.append("## Neo4j Schema")
    lines.append("")

    if constraints:
        lines.append("### Constraints")
        lines.append("")
        lines.append("| Type | Label | Property | Cypher |")
        lines.append("|------|-------|----------|--------|")
        for c in constraints:
            cypher = c.get("cypher", "").replace("|", "\\|")
            lines.append(
                f"| {c.get('type', '')} "
                f"| {c.get('label', '')} "
                f"| `{c.get('property', '')}` "
                f"| `{cypher}` |"
            )
        lines.append("")

    if indexes:
        lines.append("### Indexes")
        lines.append("")
        lines.append("| Label | Properties | Type | Cypher |")
        lines.append("|-------|-----------|------|--------|")
        for idx in indexes:
            props = ", ".join(f"`{p}`" for p in idx.get("properties", []))
            cypher = idx.get("cypher", "").replace("|", "\\|")
            lines.append(
                f"| {idx.get('label', '')} "
                f"| {props} "
                f"| {idx.get('type', '')} "
                f"| `{cypher}` |"
            )
        lines.append("")

    # ── Source Pipelines ──────────────────────────────────────────────────
    if specs:
        lines.append("## Source Pipelines")
        lines.append("")

        for spec in specs:
            sid = spec.get("source_id", "?")
            reader = spec.get("reader", {})
            config = reader.get("config", {})
            entities = spec.get("entity_extractions", [])
            rels = spec.get("relationship_extractions", [])
            upsert = spec.get("upsert_strategy", {})
            err = spec.get("error_handling", {})
            preproc = spec.get("preprocessing", [])

            label = source_label(sid)
            entity_names = [e.get("entity_type", "?") for e in entities]
            heading_target = ", ".join(entity_names) if entity_names else "—"
            lines.append(f"### {label} → {heading_target}")
            lines.append("")

            # Reader config
            fmt = reader.get("format", "?")
            conn_type = reader.get("connection_type", "file")
            delimiter = config.get("delimiter", ",")
            encoding = config.get("encoding", "utf-8")
            header_row = config.get("header_row", 0)

            lines.append("**Reader**")
            lines.append("")
            lines.append("| Setting | Value |")
            lines.append("|---------|-------|")
            lines.append(f"| Connection | {conn_type} |")
            lines.append(f"| Format | {fmt} |")
            lines.append(f"| Delimiter | `{delimiter}` |")
            lines.append(f"| Encoding | {encoding} |")
            lines.append(f"| Header row | {header_row} |")
            if reader.get("system_id"):
                lines.append(f"| System | {reader['system_id']} |")
            if reader.get("query"):
                lines.append(f"| Query | `{reader['query']}` |")
            if reader.get("endpoint"):
                lines.append(f"| Endpoint | `{reader['endpoint']}` |")
            if reader.get("incremental_field"):
                lines.append(f"| Incremental field | `{reader['incremental_field']}` |")
            lines.append("")

            # Preprocessing
            if preproc:
                lines.append("**Preprocessing**")
                lines.append("")
                for step in preproc:
                    step_name = step.get("step", "?")
                    step_desc = step.get("description", "")
                    step_config = step.get("config") or {}
                    fields = step_config.get("fields", [])

                    if fields:
                        lines.append(f"*{step_name}*: {step_desc}")
                        lines.append("")
                        lines.append("| Field | Target Type / Method |")
                        lines.append("|-------|---------------------|")
                        for f in fields:
                            fname = f.get("name", "?")
                            target = f.get("target_type", f.get("method", "?"))
                            lines.append(f"| `{fname}` | {target} |")
                        lines.append("")
                    elif step_config.get("derived_fields"):
                        lines.append(f"*{step_name}*: {step_desc}")
                        lines.append("")
                        derived = step_config["derived_fields"]
                        if isinstance(derived, dict):
                            lines.append("| Derived Field | Value / Expression |")
                            lines.append("|--------------|-------------------|")
                            for dk, dv in derived.items():
                                lines.append(f"| `{dk}` | `{dv}` |")
                            lines.append("")
                    else:
                        lines.append(f"*{step_name}*: {step_desc}")
                        lines.append("")

            # Entity extraction
            if entities:
                lines.append("**Entity Extraction**")
                lines.append("")
                lines.append("| Entity Type | ID Expression | Filter |")
                lines.append("|-------------|--------------|--------|")
                for ee in entities:
                    etype = ee.get("entity_type", "?")
                    id_expr = ee.get("id_expression", "—")
                    filt = ee.get("filter") or "—"
                    lines.append(f"| {etype} | `{id_expr}` | {filt} |")
                lines.append("")

            # Relationship extraction
            if rels:
                lines.append("**Relationship Extraction**")
                lines.append("")
                lines.append("| Relationship | From Expression | To Expression |")
                lines.append("|-------------|----------------|---------------|")
                for re_ in rels:
                    rtype = re_.get("relationship_type", "?")
                    from_e = re_.get("from_expression", "—")
                    to_e = re_.get("to_expression", "—")
                    lines.append(f"| {rtype} | `{from_e}` | `{to_e}` |")
                lines.append("")

            # Upsert + error handling
            merge_keys = ", ".join(f"`{k}`" for k in upsert.get("merge_keys", []))
            lines.append("**Load Strategy**")
            lines.append("")
            lines.append("| Setting | Value |")
            lines.append("|---------|-------|")
            lines.append(f"| Upsert mode | {upsert.get('mode', '?')} |")
            lines.append(f"| Merge keys | {merge_keys or '—'} |")
            lines.append(f"| On parse error | {err.get('on_parse_error', '?')} |")
            lines.append(f"| On constraint violation | {err.get('on_constraint_violation', '?')} |")
            if err.get("quarantine_path"):
                lines.append(f"| Quarantine path | `{err['quarantine_path']}` |")
            lines.append("")
            lines.append("---")
            lines.append("")

    # ── Incremental Strategy ──────────────────────────────────────────────
    lines.append("## Incremental Strategy")
    lines.append("")
    lines.append("| Setting | Value |")
    lines.append("|---------|-------|")
    lines.append(f"| Detection method | {incremental.get('detection_method', '?')} |")
    ts_fields = incremental.get("timestamp_fields")
    if ts_fields:
        lines.append(f"| Timestamp fields | {', '.join(f'`{f}`' for f in ts_fields)} |")
    else:
        lines.append("| Timestamp fields | None available |")
    lines.append("")
    notes = incremental.get("notes")
    if notes:
        lines.append(f"> {notes}")
        lines.append("")

    # ── Simulation Integration ────────────────────────────────────────────
    lines.append("## Simulation Integration")
    lines.append("")
    lines.append(f"**Export format:** {sim_integration.get('export_format', '?')}")
    lines.append("")

    csv_mappings = sim_integration.get("sdg_csv_mapping", [])
    if csv_mappings:
        lines.append("### SDG-Compatible CSV Exports")
        lines.append("")
        for cm in csv_mappings:
            lines.append(f"**`{cm.get('simulation_csv', '?')}`**")
            lines.append("```cypher")
            lines.append(cm.get("neo4j_query", "// TODO"))
            lines.append("```")
            lines.append("")

    profile_queries = sim_integration.get("constraint_profile_queries", [])
    if profile_queries:
        lines.append("### Constraint Profile Queries")
        lines.append("")
        for pq in profile_queries:
            lines.append(f"**`{pq.get('profile_field', '?')}`**")
            lines.append("```cypher")
            lines.append(pq.get("neo4j_query", "// TODO"))
            lines.append("```")
            lines.append("")

    sim_notes = sim_integration.get("notes")
    if sim_notes:
        lines.append(f"> {sim_notes}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Render ETL architecture YAML to PRD-style markdown."
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
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(doc)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
