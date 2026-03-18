#!/usr/bin/env python3
"""
Generate skeleton ETL scripts from a mapping plan and ETL architecture.

Produces one Python script per source file in the pipeline, with:
- Reader configuration
- Preprocessing steps (as function stubs)
- Entity extraction with Neo4j MERGE statements
- Relationship extraction with Neo4j MERGE statements
- Error handling skeleton

These are STARTING POINTS — they need human review and completion.

Usage:
    python tools/sample_etl_gen.py <architecture_path> --mapping <path> --output-dir <dir> [--verbose]

Examples:
    python tools/sample_etl_gen.py etl_architecture.yaml --mapping mapping_plan.yaml --output-dir ./etl_scripts/
"""

import argparse
import os
import sys
from pathlib import Path

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def generate_reader_code(spec: dict) -> str:
    """Generate the data reader section."""
    reader = spec.get("reader", {})
    fmt = reader.get("format", "csv")
    config = reader.get("config", {})

    if fmt in ("csv", "tsv"):
        delimiter = config.get("delimiter", "," if fmt == "csv" else "\\t")
        encoding = config.get("encoding", "utf-8")
        header_row = config.get("header_row", 0)
        skip_rows = config.get("skip_rows", 0)
        return f"""    # Read source file
    df = pd.read_csv(
        source_path,
        sep='{delimiter}',
        encoding='{encoding}',
        header={header_row},
        skiprows={skip_rows if skip_rows else 'None'},
        low_memory=False,
    )"""
    elif fmt in ("xlsx", "xls"):
        sheet = config.get("sheet_name", 0)
        header_row = config.get("header_row", 0)
        return f"""    # Read source file
    df = pd.read_excel(
        source_path,
        sheet_name='{sheet}' if '{sheet}' != '0' else 0,
        header={header_row},
    )"""
    else:
        return f"    # TODO: Implement reader for format: {fmt}"


def generate_preprocessing_code(spec: dict) -> str:
    """Generate preprocessing stubs."""
    steps = spec.get("preprocessing", [])
    if not steps:
        return "    # No preprocessing steps defined"

    lines = ["    # Preprocessing"]
    for step in steps:
        step_type = step.get("step", "unknown")
        desc = step.get("description", "")
        lines.append(f"    # {step_type}: {desc}")
        if step_type == "dedup":
            lines.append("    # df = df.drop_duplicates(subset=[...], keep='last')")
        elif step_type == "null_fill":
            lines.append("    # df[column] = df[column].fillna(default_value)")
        elif step_type == "type_coerce":
            lines.append("    # df[column] = pd.to_datetime(df[column], errors='coerce')")
        elif step_type == "filter":
            lines.append("    # df = df[df[column] != excluded_value]")
        else:
            lines.append(f"    # TODO: Implement {step_type}")

    return "\n".join(lines)


def generate_entity_code(spec: dict) -> str:
    """Generate entity extraction and upsert code."""
    extractions = spec.get("entity_extractions", [])
    upsert = spec.get("upsert_strategy", {})
    mode = upsert.get("mode", "merge")
    merge_keys = upsert.get("merge_keys", [])

    if not extractions:
        return "    # No entity extractions for this source"

    lines = ["    # Entity extraction and upsert"]
    for ext in extractions:
        entity_type = ext.get("entity_type", "Unknown")
        id_expr = ext.get("id_expression", "row['id']")
        row_filter = ext.get("filter")

        lines.append(f"")
        lines.append(f"    # --- {entity_type} ---")
        if row_filter:
            lines.append(f"    entity_df = df[{row_filter}].copy()")
        else:
            lines.append(f"    entity_df = df.copy()")

        lines.append(f"    for _, row in entity_df.iterrows():")
        lines.append(f"        try:")

        if mode == "merge":
            merge_key_str = ", ".join(f"{k}: row['{k}']" for k in merge_keys) if merge_keys else f"id: {id_expr}"
            lines.append(f"            session.run(")
            lines.append(f"                'MERGE (n:{entity_type} {{{merge_key_str}}}) '")
            lines.append(f"                'SET n += $props',")
            lines.append(f"                props=row.to_dict(),")
            lines.append(f"            )")
        else:
            lines.append(f"            # TODO: Implement {mode} upsert for {entity_type}")

        lines.append(f"        except Exception as e:")
        on_error = spec.get("error_handling", {}).get("on_constraint_violation", "skip_row")
        if on_error == "skip_row":
            lines.append(f"            errors.append(('{entity_type}', row, str(e)))")
            lines.append(f"            continue")
        elif on_error == "fail":
            lines.append(f"            raise")
        else:
            lines.append(f"            quarantine.append(('{entity_type}', row, str(e)))")

    return "\n".join(lines)


def generate_relationship_code(spec: dict) -> str:
    """Generate relationship extraction code."""
    extractions = spec.get("relationship_extractions", [])
    if not extractions:
        return "    # No relationship extractions for this source"

    lines = ["    # Relationship extraction"]
    for ext in extractions:
        rel_type = ext.get("relationship_type", "UNKNOWN")
        from_expr = ext.get("from_expression", "row['from_id']")
        to_expr = ext.get("to_expression", "row['to_id']")

        lines.append(f"")
        lines.append(f"    # --- {rel_type} ---")
        lines.append(f"    for _, row in df.iterrows():")
        lines.append(f"        try:")
        lines.append(f"            from_id = {from_expr}")
        lines.append(f"            to_id = {to_expr}")
        lines.append(f"            if from_id and to_id:")
        lines.append(f"                session.run(")
        lines.append(f"                    'MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) '")
        lines.append(f"                    'MERGE (a)-[r:{rel_type.upper()}]->(b)',")
        lines.append(f"                    from_id=str(from_id), to_id=str(to_id),")
        lines.append(f"                )")
        lines.append(f"        except Exception as e:")
        lines.append(f"            errors.append(('{rel_type}', row, str(e)))")

    return "\n".join(lines)


def generate_script(source_id: str, spec: dict) -> str:
    """Generate a complete ETL script for one source."""
    source_path_comment = spec.get("source_id", source_id)

    reader = generate_reader_code(spec)
    preprocess = generate_preprocessing_code(spec)
    entities = generate_entity_code(spec)
    relationships = generate_relationship_code(spec)

    return f'''#!/usr/bin/env python3
"""
ETL script for source: {source_path_comment}

Auto-generated skeleton — review and complete before running.
"""

import sys
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase


def process(source_path: str, neo4j_uri: str, neo4j_auth: tuple):
    """Process source file and upsert into Neo4j."""
    errors = []
    quarantine = []

{reader}

{preprocess}

    # Connect to Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)

    with driver.session() as session:
{entities}

{relationships}

    driver.close()

    # Report
    if errors:
        print(f"{{len(errors)}} errors encountered:", file=sys.stderr)
        for entity_type, row, err in errors[:10]:
            print(f"  {{entity_type}}: {{err}}", file=sys.stderr)

    if quarantine:
        print(f"{{len(quarantine)}} rows quarantined", file=sys.stderr)

    return {{"errors": len(errors), "quarantined": len(quarantine)}}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to source file")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", required=True)

    args = parser.parse_args()
    result = process(
        args.source_path,
        args.neo4j_uri,
        (args.neo4j_user, args.neo4j_password),
    )
    print(f"Done: {{result}}")
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate skeleton ETL scripts from architecture."
    )
    parser.add_argument("architecture_path", help="Path to etl_architecture.yaml")
    parser.add_argument("--mapping", help="Path to mapping_plan.yaml (for enrichment)")
    parser.add_argument("--output-dir", required=True, help="Output directory for scripts")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.architecture_path):
        print(f"File not found: {args.architecture_path}", file=sys.stderr)
        sys.exit(1)

    arch = load_yaml(args.architecture_path)
    etl = arch.get("etl_architecture", arch)
    specs = etl.get("pipeline_specs", [])

    if not specs:
        print("No pipeline specs found in architecture.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    for spec in specs:
        source_id = spec.get("source_id", "unknown")
        safe_name = source_id.replace("/", "_").replace("\\", "_").replace(".", "_")
        script_name = f"etl_{safe_name}.py"
        script_path = os.path.join(args.output_dir, script_name)

        script = generate_script(source_id, spec)

        with open(script_path, "w") as f:
            f.write(script)

        if args.verbose:
            print(f"Wrote: {script_path}", file=sys.stderr)

    print(f"Generated {len(specs)} ETL scripts in {args.output_dir}")


if __name__ == "__main__":
    main()
