# Ontograph

You are executing a data-driven ontology discovery workflow for a company.
Given a raw data room, you will catalog the data, discover the ontology,
plan the mapping, and architect the ETL pipeline.

## Engagement Setup

Check the engagement brief (`data/{company}/engagement_brief.md`) for:
- Company name and context
- **Systems table** — source systems with schema source type (ddl_file, api_docs,
  research, flat_files). This drives Phase 0 Track A.
- **Data room path** — where exported files live (if any). Drives Phase 0 Track B.
- Expected entity types (if known — these are hints, not constraints)
- Special concerns or scope limitations

**Phase 0 runs in two tracks:**
- **Track A (schema-first)**: Systems are declared → parse DDL, read API docs, or
  use playbook knowledge. Output: `system_manifest.yaml`.
- **Track B (file-based)**: Data room exists → profile files, detect joins.
  Output: `data_catalog.yaml` (with `source_profiles/`).
- **Track C (hybrid)**: Both inputs available → run both, link via `system_manifest_ref`.

FK relationships derived from DDL carry `confidence: 1.0` into Phase 1.
They are the highest-quality relationship evidence available.

## Rules

1. Read `INDEX.md` first. It defines the phase sequence, output contracts,
   and run structure.
2. Phase sequence is fixed. Do not skip phases. Do not reorder.
   Catalog → Ontology → Mapping → Architecture → Deliver.
3. Load playbooks when entering a domain. They contain recognition heuristics
   for data formats, entity types, and relationships. Do not guess where a
   playbook provides guidance.
4. Every ontology decision requires an evidence chain to specific source data.
   No unsourced entity types or relationships.
5. Gaps are first-class outputs. If you can't identify an entity type, infer
   a relationship, or map a field, say so explicitly with what's missing.
6. **Run isolation.** Prior runs are read-only. Write all outputs exclusively
   to the current run directory (`runs/{current_run}/`). Never modify a prior
   run.
7. Use deterministic tools (`tools/*.py`) for statistical profiling, join
   detection, validation, and rendering. The agent interprets tool output;
   the agent does not duplicate what tools compute.
8. The ontology is **discovered from data**, not assumed from templates.
   Domain pattern playbooks prime recognition but never prescribe. Every
   entity type and relationship must be justified by evidence in the data.
9. Decision records (D_xxxx) are required for every non-trivial ontology
   judgment. Include alternatives considered, rationale, and evidence.

## Navigation

| What | Where |
|------|-------|
| Phase DAG, output contracts, run structure | `INDEX.md` |
| Engagement context | `data/{company}/engagement_brief.md` |
| Phase instructions | `phases/` |
| Data format recognition | `playbooks/data_formats/` |
| Entity type identification | `playbooks/entity_recognition/` |
| Relationship discovery | `playbooks/relationship_inference/` |
| Industry patterns | `playbooks/domain_patterns/` |
| Known system schemas (accounting, HRIS, CRM, PM) | `playbooks/system_schemas/` |
| Structural pattern library | `patterns/` |
| Output schemas | `schemas/` |
| Deterministic tools | `tools/` |
| Run output directory | `runs/{run}/` |

## Phase Summary

### Phase 0: Catalog (agent + deterministic tools)
Two-track. **Track A (schema-first):** Parse DDL with `parse_ddl.py`, read API docs,
or use `playbooks/system_schemas/` for known systems. Detect cross-system FK relationships.
Output: `system_manifest.yaml`. **Track B (file-based):** Inventory data room, profile
tabular data, detect join keys. Output: `data_catalog.yaml` (with `source_profiles/`).
Hybrid engagements run both and link outputs via `system_manifest_ref`.

### Phase 1: Ontology Discovery (agent-driven)
Confirm/reject candidate entity types. Discover relationships. Define properties
and domain concepts. Cross-reference Simulation compatibility. Every decision
gets a decision record (D_1xxx). Output: `ontology.yaml`.

### Phase 2: Data Mapping Plan (agent-driven)
Map every ontology property to a source field. Define transformations, conflict
resolution, and statistical computations. Attest to coverage. Every mapping
decision gets a record (D_2xxx). Output: `mapping_plan.yaml`.

### Phase 3: ETL Architecture (agent + deterministic tools)
Design the pipeline DAG. Generate Neo4j schema. Specify per-source pipelines.
Define idempotency and Simulation integration. Output: `etl_architecture.yaml`,
`neo4j_schema.cypher`.

### Phase 4: Deliver (deterministic tools)
Render all YAML artifacts into human-readable documents. Output: `delivery/`.

## Tool Usage

All tools are stateless, take file paths as arguments, and produce YAML/JSON output.

| Tool | Phase | Purpose |
|------|-------|---------|
| `parse_ddl.py` | 0A | Parse SQL DDL → structured schema metadata (tables, columns, FKs) |
| `profile_source.py` | 0B | Statistical profile of a tabular source |
| `detect_joins.py` | 0B | Join-key candidates across sources |
| `validate_catalog.py` | 0 | Catalog completeness check |
| `validate_ontology.py` | 1 | Ontology internal consistency |
| `validate_mapping.py` | 2 | Mapping coverage check |
| `validate_evidence.py` | All | Evidence chains resolve to source data |
| `neo4j_schema_gen.py` | 3 | Ontology YAML to Cypher DDL |
| `sample_etl_gen.py` | 3 | Mapping plan to skeleton ETL scripts |
| `render_ontology.py` | 4 | Ontology to readable document |
| `render_mapping.py` | 4 | Mapping plan to readable document |
| `render_architecture.py` | 4 | ETL architecture to readable document |

## Integration with Simulation

Phase 1 produces a `simulation_compatibility` section that maps discovered
ontology types to Simulation's graph contract (Person, Department, Initiative,
CustomerContract, etc.). Phase 3 produces a `simulation_integration` section
specifying how the Neo4j graph exports data for Basin consumption.

The ontology reflects the data — it is not forced to match Simulation's types.
Compatibility gaps are tracked explicitly so they can be addressed through either
Simulation extension or data enrichment.
