#!/usr/bin/env python3
"""
Validate an ontology for internal consistency.

Checks:
1. Every entity type has at least one source
2. Every entity type participates in at least one relationship
3. Every relationship references valid entity types
4. No orphan entity types
5. Identifiers are defined for all entity types
6. Property types are valid
7. Simulation compatibility section is present

Usage:
    python tools/validate_ontology.py <ontology_path> [--verbose]

Exit codes:
    0 = all checks pass
    1 = validation failures found
"""

import argparse
import os
import sys

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate(ontology_path: str, verbose: bool) -> list[str]:
    """Run all validation checks. Returns list of failure messages."""
    failures = []

    try:
        data = load_yaml(ontology_path)
    except Exception as e:
        return [f"Cannot parse ontology YAML: {e}"]

    ontology = data.get("ontology", data)

    # Check required sections
    for section in ["metadata", "entity_types", "relationship_types"]:
        if section not in ontology:
            failures.append(f"Missing required section: {section}")

    entity_types = ontology.get("entity_types", [])
    relationship_types = ontology.get("relationship_types", [])
    entity_names = {et.get("name") for et in entity_types}

    # Check 1: Every entity type has sources
    for et in entity_types:
        name = et.get("name", "<unnamed>")
        if not et.get("sources"):
            failures.append(f"Entity type '{name}' has no sources")

    # Check 2: Every entity type has an identifier
    for et in entity_types:
        name = et.get("name", "<unnamed>")
        ident = et.get("identifier", {})
        if not ident.get("property"):
            failures.append(f"Entity type '{name}' has no identifier property")

    # Check 3: Property types are valid
    valid_types = {"string", "integer", "float", "date", "boolean", "list"}
    for et in entity_types:
        name = et.get("name", "<unnamed>")
        for prop in et.get("properties", []):
            ptype = prop.get("type", "")
            if ptype and ptype not in valid_types:
                failures.append(
                    f"Entity type '{name}', property '{prop.get('name')}': "
                    f"invalid type '{ptype}' (valid: {valid_types})"
                )

    # Check 4: Relationships reference valid entity types
    for rt in relationship_types:
        rname = rt.get("name", "<unnamed>")
        from_type = rt.get("from_type", "")
        to_type = rt.get("to_type", "")
        if from_type and from_type not in entity_names:
            failures.append(
                f"Relationship '{rname}': from_type '{from_type}' not in entity types"
            )
        if to_type and to_type not in entity_names:
            failures.append(
                f"Relationship '{rname}': to_type '{to_type}' not in entity types"
            )

    # Check 5: No orphan entity types (every type in at least one relationship)
    connected_types = set()
    for rt in relationship_types:
        connected_types.add(rt.get("from_type"))
        connected_types.add(rt.get("to_type"))

    for et in entity_types:
        name = et.get("name")
        if name and name not in connected_types:
            failures.append(f"Orphan entity type: '{name}' has no relationships")

    # Check 6: Relationship cardinality is valid
    valid_cardinalities = {"1:1", "1:N", "N:1", "N:M"}
    for rt in relationship_types:
        rname = rt.get("name", "<unnamed>")
        card = rt.get("cardinality", "")
        if card and card not in valid_cardinalities:
            failures.append(
                f"Relationship '{rname}': invalid cardinality '{card}'"
            )

    # Check 7: Relationships have evidence
    for rt in relationship_types:
        rname = rt.get("name", "<unnamed>")
        if not rt.get("evidence"):
            failures.append(f"Relationship '{rname}' has no evidence")

    # Check 8: Simulation compatibility section
    if "simulation_compatibility" not in ontology:
        failures.append("Missing simulation_compatibility section")

    # Check 9: Entity types have evidence
    for et in entity_types:
        name = et.get("name", "<unnamed>")
        if not et.get("evidence"):
            failures.append(f"Entity type '{name}' has no evidence")

    if verbose and not failures:
        print(f"  OK: {len(entity_types)} entity types, "
              f"{len(relationship_types)} relationships", file=sys.stderr)

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Validate ontology internal consistency."
    )
    parser.add_argument("ontology_path", help="Path to ontology.yaml")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.ontology_path):
        print(f"File not found: {args.ontology_path}", file=sys.stderr)
        sys.exit(1)

    failures = validate(args.ontology_path, args.verbose)

    if failures:
        print(f"FAIL: {len(failures)} validation failure(s):\n")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("PASS: All ontology validation checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
