#!/usr/bin/env python3
"""
Generate Neo4j Cypher DDL from an ontology YAML.

Produces:
- CREATE CONSTRAINT statements for uniqueness on entity identifiers
- CREATE INDEX statements for frequently-queried properties
- Comments documenting the schema

Usage:
    python tools/neo4j_schema_gen.py <ontology_path> [--output <path>] [--verbose]

Examples:
    python tools/neo4j_schema_gen.py runs/acme_20260317/phase_1_ontology/ontology.yaml
    python tools/neo4j_schema_gen.py ontology.yaml --output neo4j_schema.cypher
"""

import argparse
import os
import sys
from datetime import datetime

import yaml


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def type_to_neo4j(prop_type: str) -> str:
    """Map ontology property types to Neo4j-friendly descriptions."""
    mapping = {
        "string": "STRING",
        "integer": "INTEGER",
        "float": "FLOAT",
        "date": "DATE",
        "boolean": "BOOLEAN",
        "list": "LIST<STRING>",
    }
    return mapping.get(prop_type, "STRING")


def generate_schema(ontology_path: str, verbose: bool) -> tuple[str, dict]:
    """Generate Cypher DDL and structured schema dict."""
    data = load_yaml(ontology_path)
    onto = data.get("ontology", data)

    entity_types = onto.get("entity_types", [])
    relationship_types = onto.get("relationship_types", [])

    lines = []
    constraints = []
    indexes = []

    # Header
    lines.append(f"// Neo4j Schema generated from ontology")
    lines.append(f"// Source: {ontology_path}")
    lines.append(f"// Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"// Entity types: {len(entity_types)}")
    lines.append(f"// Relationship types: {len(relationship_types)}")
    lines.append("")

    # Constraints
    lines.append("// === UNIQUENESS CONSTRAINTS ===")
    lines.append("")

    for et in entity_types:
        name = et.get("name", "")
        ident = et.get("identifier", {})
        id_prop = ident.get("property", "")

        if name and id_prop:
            constraint_name = f"uniq_{name.lower()}_{id_prop}"
            cypher = (
                f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
                f"FOR (n:{name}) REQUIRE n.{id_prop} IS UNIQUE;"
            )
            lines.append(f"// {name} — unique on {id_prop}")
            lines.append(cypher)
            lines.append("")

            constraints.append({
                "type": "uniqueness",
                "label": name,
                "property": id_prop,
                "cypher": cypher,
            })

    # Indexes
    lines.append("// === INDEXES ===")
    lines.append("")

    for et in entity_types:
        name = et.get("name", "")
        props = et.get("properties", [])

        # Index date fields, status/state fields, name fields
        indexable_keywords = ["date", "status", "state", "name", "type", "level"]
        for prop in props:
            pname = prop.get("name", "")
            ptype = prop.get("type", "")

            should_index = (
                ptype == "date"
                or any(kw in pname.lower() for kw in indexable_keywords)
            )

            if should_index and pname != et.get("identifier", {}).get("property"):
                idx_type = "RANGE" if ptype in ("date", "integer", "float") else "BTREE"
                idx_name = f"idx_{name.lower()}_{pname}"
                cypher = (
                    f"CREATE INDEX {idx_name} IF NOT EXISTS "
                    f"FOR (n:{name}) ON (n.{pname});"
                )
                lines.append(f"// {name}.{pname} ({idx_type})")
                lines.append(cypher)
                lines.append("")

                indexes.append({
                    "label": name,
                    "properties": [pname],
                    "type": idx_type.lower(),
                    "cypher": cypher,
                })

    # Relationship documentation
    lines.append("// === RELATIONSHIP TYPES ===")
    lines.append("// (No DDL needed — relationships are created implicitly)")
    lines.append("")

    for rt in relationship_types:
        rname = rt.get("name", "")
        from_type = rt.get("from_type", "")
        to_type = rt.get("to_type", "")
        card = rt.get("cardinality", "")
        rel_props = rt.get("properties", [])

        prop_desc = ""
        if rel_props:
            prop_names = [p.get("name", "") for p in rel_props]
            prop_desc = f" — properties: {', '.join(prop_names)}"

        lines.append(
            f"// (:{from_type})-[:{rname.upper()}]->(:{to_type}) "
            f"[{card}]{prop_desc}"
        )

    lines.append("")
    lines.append(f"// Total: {len(constraints)} constraints, {len(indexes)} indexes, "
                 f"{len(relationship_types)} relationship types")

    cypher_text = "\n".join(lines)

    schema_dict = {
        "constraints": constraints,
        "indexes": indexes,
    }

    if verbose:
        print(f"Generated: {len(constraints)} constraints, {len(indexes)} indexes",
              file=sys.stderr)

    return cypher_text, schema_dict


def main():
    parser = argparse.ArgumentParser(
        description="Generate Neo4j Cypher DDL from ontology."
    )
    parser.add_argument("ontology_path", help="Path to ontology.yaml")
    parser.add_argument("--output", "-o", help="Output .cypher file path")
    parser.add_argument("--output-yaml", help="Output schema YAML path")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.ontology_path):
        print(f"File not found: {args.ontology_path}", file=sys.stderr)
        sys.exit(1)

    cypher_text, schema_dict = generate_schema(args.ontology_path, args.verbose)

    if args.output:
        with open(args.output, "w") as f:
            f.write(cypher_text)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(cypher_text)

    if args.output_yaml:
        with open(args.output_yaml, "w") as f:
            yaml.dump(schema_dict, f, default_flow_style=False, sort_keys=False)
        if args.verbose:
            print(f"Wrote: {args.output_yaml}", file=sys.stderr)


if __name__ == "__main__":
    main()
