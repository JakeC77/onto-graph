# Phase 4: Deliver

Render all machine-readable artifacts into human-reviewable documents.
This phase is fully deterministic — it transforms YAML outputs from
Phases 0-3 into readable markdown documents.

## Context Manifest

Load before starting:
- This file
- Phase 1 output: `{run}/phase_1_ontology/ontology.yaml`
- Phase 2 output: `{run}/phase_2_mapping/mapping_plan.yaml`
- Phase 3 output: `{run}/phase_3_architecture/etl_architecture.yaml`
- Phase 3 output: `{run}/phase_3_architecture/neo4j_schema.cypher`

---

## Operations

Four operations. All use deterministic rendering tools.

### 4.1: Render Ontology Document

Run `tools/render_ontology.py` on `ontology.yaml` to produce:

- Entity type catalog with descriptions, properties, and sources
- Relationship type catalog with cardinality, direction, and evidence
- Domain concept glossary
- Entity-relationship diagram (Mermaid format)
- Simulation compatibility matrix

The document should be readable by someone unfamiliar with the ontology —
clear descriptions, no raw YAML structure exposed.

**Output**: `delivery/ontology_document.md`

### 4.2: Render Mapping Document

Run `tools/render_mapping.py` on `mapping_plan.yaml` to produce:

- Source-to-entity mapping tables
- Field-level mapping detail (per entity type)
- Gap inventory with downstream impact
- Statistical computation specifications
- Source utilization summary

**Output**: `delivery/mapping_document.md`

### 4.3: Render Architecture Document

Run `tools/render_architecture.py` on `etl_architecture.yaml` to produce:

- Pipeline DAG diagram (Mermaid format)
- Neo4j schema documentation
- Per-source pipeline specifications summary
- Idempotency and incremental strategy
- Simulation integration specification

**Output**: `delivery/architecture_document.md`

### 4.4: Generate Delivery Manifest

List all delivery artifacts with their purpose:

- `ontology_document.md` — What the ontology looks like
- `mapping_document.md` — How data maps to the ontology
- `architecture_document.md` — How to build the pipeline
- `neo4j_schema.cypher` — Ready-to-run schema DDL
- Decision records — Audit trail for all judgments

**Output**: `delivery/delivery_manifest.md`

---

## Self-Validation

After rendering:

1. All three documents exist and are non-empty
2. Mermaid diagrams render correctly (valid syntax)
3. All entity types from the ontology appear in the ontology document
4. All sources from the catalog appear in the mapping document
5. Delivery manifest lists all artifacts

---

## Audience Model

- **Decision-maker** reads the ontology document (entity types, relationships,
  key domain concepts) and the executive summary sections of mapping and
  architecture documents
- **Data engineer** works through the full mapping document and architecture
  document to implement the pipeline
- **Analyst** references the domain concept glossary and the gap inventory
  to understand what's known and what's missing
