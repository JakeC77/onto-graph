#!/usr/bin/env python3
"""
Render an ontology YAML into a human-readable markdown document.

Produces:
- Entity type catalog
- Relationship type catalog
- Domain concept glossary
- Entity-relationship diagram (Mermaid)
- Simulation compatibility matrix

Usage:
    python tools/render_ontology.py <ontology_path> [--output <path>] [--verbose]
"""

import argparse
import os
import sys
from datetime import datetime

import yaml


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def render(ontology_path: str, verbose: bool) -> str:
    data = load_yaml(ontology_path)
    onto = data.get("ontology", data)

    meta = onto.get("metadata", {})
    entity_types = onto.get("entity_types", [])
    relationship_types = onto.get("relationship_types", [])
    domain_concepts = onto.get("domain_concepts", [])
    sim_compat = onto.get("simulation_compatibility", {})

    lines = []

    # Header
    lines.append(f"# Ontology — {meta.get('company', 'Unknown Company')}")
    lines.append("")
    lines.append(f"Generated from `{ontology_path}` on {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"- **Entity types:** {len(entity_types)}")
    lines.append(f"- **Relationship types:** {len(relationship_types)}")
    lines.append(f"- **Domain concepts:** {len(domain_concepts)}")
    lines.append("")

    # Entity-Relationship Diagram
    lines.append("## Entity-Relationship Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("erDiagram")
    for rt in relationship_types:
        from_t = rt.get("from_type", "?")
        to_t = rt.get("to_type", "?")
        card = rt.get("cardinality", "")
        rname = rt.get("name", "")

        # Map cardinality to Mermaid notation
        card_map = {
            "1:1": "||--||",
            "1:N": "||--o{",
            "N:1": "}o--||",
            "N:M": "}o--o{",
        }
        mermaid_card = card_map.get(card, "||--||")
        lines.append(f"    {from_t} {mermaid_card} {to_t} : {rname}")

    lines.append("```")
    lines.append("")

    # Entity Types
    lines.append("## Entity Types")
    lines.append("")

    for et in entity_types:
        name = et.get("name", "Unknown")
        desc = et.get("description", "")
        ident = et.get("identifier", {})
        props = et.get("properties", [])
        lifecycle = et.get("lifecycle", {})
        sources = et.get("sources", [])
        count = et.get("instance_count", "?")

        lines.append(f"### {name}")
        lines.append("")
        lines.append(desc)
        lines.append("")
        lines.append(f"- **Identifier:** `{ident.get('property', '?')}` ({ident.get('pattern', '')})")
        lines.append(f"- **Instance count:** {count}")
        lines.append(f"- **Sources:** {', '.join(sources) if sources else 'none'}")

        if lifecycle.get("states"):
            lines.append(f"- **Lifecycle states:** {', '.join(lifecycle['states'])}")

        lines.append("")

        if props:
            lines.append("| Property | Type | Required | Source | Description |")
            lines.append("|----------|------|----------|--------|-------------|")
            for p in props:
                lines.append(
                    f"| `{p.get('name', '')}` "
                    f"| {p.get('type', '')} "
                    f"| {'Yes' if p.get('required') else 'No'} "
                    f"| {p.get('source', '')} "
                    f"| {p.get('description', '')} |"
                )
            lines.append("")

    # Relationship Types
    lines.append("## Relationship Types")
    lines.append("")
    lines.append("| Relationship | From | To | Cardinality | Method | Confidence |")
    lines.append("|-------------|------|-----|------------|--------|-----------|")

    for rt in relationship_types:
        lines.append(
            f"| `{rt.get('name', '')}` "
            f"| {rt.get('from_type', '')} "
            f"| {rt.get('to_type', '')} "
            f"| {rt.get('cardinality', '')} "
            f"| {rt.get('discovery_method', '')} "
            f"| {rt.get('confidence', '')} |"
        )

    lines.append("")

    # Relationship details
    for rt in relationship_types:
        rname = rt.get("name", "")
        rel_props = rt.get("properties", [])
        if rel_props:
            lines.append(f"**{rname}** properties:")
            for p in rel_props:
                lines.append(f"- `{p.get('name', '')}` ({p.get('type', '')})")
            lines.append("")

    # Domain Concepts
    if domain_concepts:
        lines.append("## Domain Concepts")
        lines.append("")
        lines.append("| Concept | Entity Type | Definition |")
        lines.append("|---------|------------|------------|")
        for dc in domain_concepts:
            values = dc.get("values")
            val_str = f" Values: {', '.join(values)}" if values else ""
            lines.append(
                f"| **{dc.get('name', '')}** "
                f"| {dc.get('entity_type', '')} "
                f"| {dc.get('definition', '')}{val_str} |"
            )
        lines.append("")

    # Simulation Compatibility
    lines.append("## Simulation Compatibility")
    lines.append("")

    matched_nodes = sim_compat.get("matched_node_types", [])
    if matched_nodes:
        lines.append("### Matched Node Types")
        lines.append("")
        lines.append("| Ontology Type | Simulation Type |")
        lines.append("|-------------|----------------|")
        for m in matched_nodes:
            lines.append(f"| {m.get('ontology_type', '')} | {m.get('simulation_type', '')} |")
        lines.append("")

    matched_edges = sim_compat.get("matched_edge_types", [])
    if matched_edges:
        lines.append("### Matched Edge Types")
        lines.append("")
        lines.append("| Ontology Type | Simulation Type |")
        lines.append("|-------------|----------------|")
        for m in matched_edges:
            lines.append(f"| {m.get('ontology_type', '')} | {m.get('simulation_type', '')} |")
        lines.append("")

    unmapped = sim_compat.get("unmapped_ontology_types", [])
    if unmapped:
        lines.append(f"### Unmapped Ontology Types")
        lines.append("")
        for t in unmapped:
            lines.append(f"- {t}")
        lines.append("")

    missing = sim_compat.get("missing_simulation_types", [])
    if missing:
        lines.append(f"### Missing Simulation Types (expected but not in data)")
        lines.append("")
        for t in missing:
            lines.append(f"- {t}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Render ontology YAML to human-readable markdown."
    )
    parser.add_argument("ontology_path", help="Path to ontology.yaml")
    parser.add_argument("--output", "-o", help="Output markdown path")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.ontology_path):
        print(f"File not found: {args.ontology_path}", file=sys.stderr)
        sys.exit(1)

    doc = render(args.ontology_path, args.verbose)

    if args.output:
        with open(args.output, "w") as f:
            f.write(doc)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
