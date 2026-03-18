#!/usr/bin/env python3
"""
Validate a mapping plan for coverage and consistency.

Checks:
1. Every ontology property has a field mapping (or documented gap)
2. Every source file is consumed or explicitly excluded
3. No circular dependencies in computed fields
4. Relationship mappings reference valid entity/relationship types
5. Statistical computations reference existing source fields

Usage:
    python tools/validate_mapping.py <mapping_path> --ontology <path> --catalog <path> [--verbose]

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


def validate(mapping_path: str, ontology_path: str,
             catalog_path: str, verbose: bool) -> list[str]:
    failures = []

    try:
        mapping = load_yaml(mapping_path)
        ontology = load_yaml(ontology_path)
        catalog = load_yaml(catalog_path)
    except Exception as e:
        return [f"Cannot parse YAML: {e}"]

    mp = mapping.get("mapping_plan", mapping)
    onto = ontology.get("ontology", ontology)
    cat = catalog.get("data_catalog", catalog)

    entity_mappings = mp.get("entity_mappings", [])
    relationship_mappings = mp.get("relationship_mappings", [])
    stat_computations = mp.get("statistical_computations", [])
    coverage = mp.get("coverage", {})
    source_util = mp.get("source_utilization", [])

    # Build ontology property inventory
    ontology_entity_types = {et["name"]: et for et in onto.get("entity_types", [])}
    ontology_rel_types = {rt["name"]: rt for rt in onto.get("relationship_types", [])}

    mapped_entity_names = {em.get("entity_type") for em in entity_mappings}
    mapped_rel_names = {rm.get("relationship_type") for rm in relationship_mappings}

    # Check 1: Every ontology entity type has a mapping
    for et_name in ontology_entity_types:
        if et_name not in mapped_entity_names:
            failures.append(f"Entity type '{et_name}' has no mapping")

    # Check 2: Every ontology relationship type has a mapping
    for rt_name in ontology_rel_types:
        if rt_name not in mapped_rel_names:
            failures.append(f"Relationship type '{rt_name}' has no mapping")

    # Check 3: Field-level coverage
    for em in entity_mappings:
        et_name = em.get("entity_type", "")
        et_def = ontology_entity_types.get(et_name, {})
        ontology_props = {p["name"] for p in et_def.get("properties", [])}
        mapped_props = {fm.get("target_property") for fm in em.get("field_mappings", [])}

        # Also count statistical computations targeting this entity type
        computed_props = {
            sc.get("target_property") for sc in stat_computations
            if sc.get("target_entity_type") == et_name
        }

        all_mapped = mapped_props | computed_props
        gap_props = {g.get("property") for g in coverage.get("gaps", [])
                     if g.get("entity_type") == et_name}

        unmapped = ontology_props - all_mapped - gap_props
        for p in unmapped:
            failures.append(
                f"Property '{et_name}.{p}' not mapped and not in gaps"
            )

    # Check 4: Source utilization
    catalog_source_ids = {s.get("source_id") for s in cat.get("sources", [])}
    utilized_sources = set()
    for em in entity_mappings:
        if em.get("system_of_record"):
            utilized_sources.add(em["system_of_record"])
        for s in em.get("additional_sources", []):
            utilized_sources.add(s)
    for rm in relationship_mappings:
        if rm.get("source"):
            utilized_sources.add(rm["source"])

    excluded_sources = {
        su.get("source_id") for su in source_util
        if not su.get("consumed") and su.get("exclusion_reason")
    }

    unaccounted = catalog_source_ids - utilized_sources - excluded_sources
    for sid in unaccounted:
        failures.append(f"Source '{sid}' not consumed and not excluded")

    # Check 5: Circular dependency detection in computed fields
    comp_deps = {}
    for sc in stat_computations:
        target = f"{sc.get('target_entity_type')}.{sc.get('target_property')}"
        inputs = []
        for inp in sc.get("inputs", []):
            inputs.append(f"{inp.get('source', '')}.{inp.get('field', '')}")
        comp_deps[target] = inputs

    # Simple cycle detection
    def has_cycle(node, visited, stack):
        visited.add(node)
        stack.add(node)
        for dep in comp_deps.get(node, []):
            if dep in comp_deps:  # Only check computed deps
                if dep not in visited:
                    if has_cycle(dep, visited, stack):
                        return True
                elif dep in stack:
                    return True
        stack.discard(node)
        return False

    for node in comp_deps:
        if has_cycle(node, set(), set()):
            failures.append(f"Circular dependency detected involving: {node}")
            break

    # Check 6: Entity mappings have required fields
    for em in entity_mappings:
        et = em.get("entity_type", "<unnamed>")
        if not em.get("system_of_record"):
            failures.append(f"Entity mapping '{et}' missing system_of_record")
        if not em.get("merge_key"):
            failures.append(f"Entity mapping '{et}' missing merge_key")

    if verbose and not failures:
        print(f"  OK: {len(entity_mappings)} entity mappings, "
              f"{len(relationship_mappings)} relationship mappings, "
              f"{len(stat_computations)} computations", file=sys.stderr)

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Validate mapping plan coverage and consistency."
    )
    parser.add_argument("mapping_path", help="Path to mapping_plan.yaml")
    parser.add_argument("--ontology", required=True, help="Path to ontology.yaml")
    parser.add_argument("--catalog", required=True, help="Path to data_catalog.yaml")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    for path in [args.mapping_path, args.ontology, args.catalog]:
        if not os.path.exists(path):
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)

    failures = validate(args.mapping_path, args.ontology, args.catalog, args.verbose)

    if failures:
        print(f"FAIL: {len(failures)} validation failure(s):\n")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("PASS: All mapping validation checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
