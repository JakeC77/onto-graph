# INDEX — Ontograph

## Phase DAG

```
Catalog → Ontology → Mapping → Architecture → Deliver
  │          │          │           │             │
  │          │          │           │             └─ Delivery Package
  │          │          │           └─ ETL Architecture + Neo4j Schema
  │          │          └─ Mapping Plan + Statistical Specs
  │          └─ Ontology + Decision Records
  └─ Data Catalog + Source Profiles
```

Each phase produces artifacts that subsequent phases consume.
Phase sequence is fixed. Within each phase, execution follows the
priority established by data quality and coverage signals from Phase 0.

## Phase Design Gradient

Phases increase in analytical freedom as they progress:

- **Catalog** — Mechanical. Two-track: schema-first (parse DDL / research) +
  file-based (inventory, profile, detect joins).
- **Ontology** — Structured. Playbooks guide entity/relationship
  recognition. Specific types discovered from the data.
- **Mapping** — Prescriptive. Every ontology property must have a
  mapping or a documented gap.
- **Architecture** — Engineering. Pipeline design, schema generation,
  integration specification.
- **Deliver** — Mechanical. Render YAML artifacts into documents.

## Decision Types

- **D_1xxx** = Phase 1 (Ontology) — entity classification, relationship
  direction, property typing, domain concept definition
- **D_2xxx** = Phase 2 (Mapping) — source-of-record selection, conflict
  resolution strategy, transformation choice, statistical method
- **D_3xxx** = Phase 3 (Architecture) — pipeline topology, upsert
  strategy, incremental approach, integration format

## Run Structure

```
runs/{company}_{timestamp}/
  phase_0_catalog/
    system_manifest.yaml         # Track A output
    data_catalog.yaml            # Track B output (+ system_manifest_ref if hybrid)
    schemas/
      {system_id}.yaml           # parse_ddl.py output per system
    source_profiles/
      {source_name}_profile.yaml
      ...
  phase_1_ontology/
    ontology.yaml
    decisions/
      D_1001.yaml
      ...
    entity_type_evidence/
    relationship_type_evidence/
  phase_2_mapping/
    mapping_plan.yaml
    statistical_specs/
    decisions/
      D_2001.yaml
      ...
  phase_3_architecture/
    etl_architecture.yaml
    neo4j_schema.cypher
    pipeline_specs/
    decisions/
      D_3001.yaml
      ...
  delivery/
    ontology_document.md
    mapping_document.md
    architecture_document.md
    delivery_manifest.md
```

## Output Contracts

Each phase's primary output must conform to its schema in `schemas/`.

| Phase | Primary Output | Schema |
|-------|---------------|--------|
| 0A — Catalog (schema-first) | `system_manifest.yaml` | `schemas/system_manifest.yaml` |
| 0B — Catalog (file-based) | `data_catalog.yaml` | `schemas/data_catalog.yaml` |
| 1 — Ontology | `ontology.yaml` | `schemas/ontology.yaml` |
| 2 — Mapping | `mapping_plan.yaml` | `schemas/mapping_plan.yaml` |
| 3 — Architecture | `etl_architecture.yaml` | `schemas/etl_architecture.yaml` |
| All | Decision records | `schemas/decision.yaml` |
| All | Evidence chains | `schemas/evidence.yaml` |

## Self-Validation Gates

Each phase has validation checks that must pass before proceeding.

**Phase 0 (Track A):** Every declared system has an entry in `system_manifest.yaml`.
Every system has `schema_confidence` set. Cross-system relationships documented.
**Phase 0 (Track B):** Every file in data room inventoried. Every tabular source
profiled. Join candidates identified. Gaps documented.

**Phase 1:** Every entity type has source evidence. Every relationship has
evidence. No orphan types. Decision records for all non-trivial judgments.
Simulation compatibility matrix complete.

**Phase 2:** 100% property coverage (mapped or gap-documented). 100% source
utilization (consumed or explicitly excluded). No circular computed-field
dependencies. Statistical specs are computable.

**Phase 3:** Pipeline DAG is acyclic. Every mapping has a pipeline step. Neo4j
schema covers all ontology types. Upsert strategies defined. Simulation
integration specified.
