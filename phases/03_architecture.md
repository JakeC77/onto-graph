# Phase 3: ETL Architecture

Design the pipeline that executes the mapping plan. By the end of this phase,
you have a complete engineering blueprint: Neo4j schema, pipeline DAG, per-source
pipeline specs, and Simulation integration specification.

This is the "how to get it there" specification. Phase 2 defined "what goes where."

## Context Manifest

Load before starting:
- This file
- `schemas/etl_architecture.yaml`
- `schemas/decision.yaml`
- Phase 1 output: `{run}/phase_1_ontology/ontology.yaml`
- Phase 2 output: `{run}/phase_2_mapping/mapping_plan.yaml`
- Phase 0 catalog: `{run}/phase_0_catalog/data_catalog.yaml` (Track B, if exists)
- Phase 0 system manifest: `{run}/phase_0_catalog/system_manifest.yaml` (Track A, if exists)

---

## Operations

Five operations. Mix of agent-driven design and deterministic tool output.

### 3.1: Pipeline Topology

Design the execution DAG — what runs in what order:

**Stage types:**
- `ingest` — Read source files into intermediate representation
- `transform` — Apply mappings, transformations, computations
- `load` — Upsert into Neo4j
- `validate` — Post-load integrity checks

**Ordering rules:**
1. Entity nodes before relationship edges (can't create edges without endpoints)
2. Parent entity types before child types (Department before Person if Person.member_of references Department)
3. Independent entity types can be loaded in parallel
4. Computed properties after their input entities are loaded
5. Validation after all loads complete

Draw the DAG explicitly: which stages depend on which.

**Output**: `pipeline_dag` section of `etl_architecture.yaml`

### 3.2: Neo4j Schema Generation

Run `tools/neo4j_schema_gen.py` on the ontology to produce Cypher DDL:

- **Node labels**: One per entity type
- **Relationship types**: One per relationship type
- **Uniqueness constraints**: On each entity type's identifier property
- **Indexes**: On frequently-queried properties (date fields, status fields,
  name fields, FK-like properties)
- **Node key constraints**: For composite identifiers (if any)

Review the generated schema for:
- Index types (btree for equality, fulltext for text search, range for comparisons)
- Constraint coverage (every entity type should have at least a uniqueness constraint)

**Output**: `neo4j_schema` section of `etl_architecture.yaml` + `neo4j_schema.cypher` file

### 3.3: Per-Source Pipeline Specifications

For each source (file, database table, or API endpoint), specify the complete
processing pipeline:

**Reader configuration:**

*File reader (Track B):*
- Format (csv, xlsx, json, etc.)
- Format-specific config: delimiter, sheet name, encoding, header row, skip rows
- (From Phase 0 profiles — copy relevant details)

*Database reader (Track A — `schema_source: ddl_file`):*
- `connection_type: database_query`
- `system_id`: which system (from system manifest)
- `query`: SQL SELECT to extract the table (e.g., `SELECT * FROM Invoice WHERE ...`)
- `incremental_field`: timestamp or sequence column for incremental runs (if any)
- Note: Actual connection credentials are NOT specified here — that's runtime config.
  Specify the logical query; connection parameters are injected at runtime.

*API reader (Track A — `schema_source: api_docs`):*
- `connection_type: api_call`
- `system_id`: which system (from system manifest)
- `endpoint`: REST path (e.g., `/rest/v1.0/projects`)
- `method`: GET (typically)
- `pagination_type`: offset, cursor, or page
- `rate_limit_notes`: any known rate limits to respect
- Note: API credentials are NOT specified here — injected at runtime.

**Preprocessing steps:**
- Deduplication (on which key?)
- Null handling (fill, drop, quarantine?)
- Type coercion (which columns need casting?)
- Normalization (trim whitespace, standardize casing?)
- Filtering (which rows to exclude?)

**Entity extractions:**
- Which entity type does this source produce?
- Row filter (if not all rows → entities)
- ID expression: how to compute the node ID from source fields

**Relationship extractions:**
- Which relationships does this source produce?
- From-expression: how to resolve the source entity
- To-expression: how to resolve the target entity

**Upsert strategy:**
- `merge` — MERGE on identifier, SET properties (idempotent)
- `create_or_skip` — CREATE if not exists, skip if exists
- `replace` — DELETE + CREATE (destructive, use carefully)
- Merge keys: which properties to match on

**Error handling:**
- On parse error: skip_row, fail_pipeline, quarantine
- On constraint violation: skip_row, fail_pipeline, quarantine
- Quarantine path: where bad rows go for review

Write decision records (D_3xxx) for upsert strategy choices and error
handling approaches.

**Output**: `pipeline_specs` section of `etl_architecture.yaml` + `pipeline_specs/` directory

### 3.4: Idempotency and Incremental Strategy

Specify how re-runs and updates work:

- **Full reload**: Delete all, reload from scratch. Simplest but slowest.
- **Timestamp-based incremental**: Only process records newer than last run.
  Requires: timestamp field in source, last-run timestamp storage.
  For database readers: use `WHERE updated_at > last_run_ts` in the query.
  For API readers: use modified_since or date-filter query parameters if available.
- **Hash-based incremental**: Compute hash of each record, skip unchanged.
  Requires: hash computation, hash storage.
- **Full scan with merge**: Read everything, MERGE all records. Idempotent
  but reads everything.

For the initial implementation, recommend full scan with merge (simplest,
idempotent, no state management). Note what would be needed for incremental.

**Output**: `incremental_strategy` section of `etl_architecture.yaml`

### 3.5: Simulation Integration Specification

Define how Basin/Simulation consumes the Neo4j graph:

**Option A: SDG-compatible CSV export**
For each of Simulation's required CSVs (employees.csv, org_structure.csv,
initiatives.csv, contracts.csv, etc.), provide a Cypher query that exports
matching data from Neo4j.

**Option B: Direct Neo4j queries**
Simulation queries Neo4j directly. Provide the query patterns.

**Constraint profile generation:**
For each field in Simulation's per-entity constraint profiles, provide
the Neo4j query that computes it:
- Knowledge boundaries → from entity properties + relationship counts
- Behavioral parameters → from computed properties (Phase 2 specs)
- Decision authority → from approval relationships and financial thresholds

Write a decision record (D_3xxx) for the integration format choice.

**Output**: `simulation_integration` section of `etl_architecture.yaml`

---

## Self-Validation

Before proceeding to Phase 4, verify:

1. Pipeline DAG is acyclic (no circular dependencies)
2. Every mapping in Phase 2 has a corresponding pipeline step
3. Neo4j schema covers all entity types and relationship types
4. Upsert strategies are defined for all entity types
5. Error handling is specified for all sources
6. Simulation integration path is specified
7. `etl_architecture.yaml` conforms to `schemas/etl_architecture.yaml`

---

## What NOT to Do

- Don't write actual ETL code yet — just specify what the code should do
- Don't optimize prematurely — start with simple, correct, idempotent
- Don't ignore error handling — messy data WILL have parse errors
- Don't couple to a specific orchestration tool (Airflow, Dagster, etc.) —
  just define the logical DAG
