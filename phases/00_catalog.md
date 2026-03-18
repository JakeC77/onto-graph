# Phase 0: Catalog

Inventory the data available for this engagement. By the end of this phase,
you know every source that exists, what it contains, how sources relate to
each other, what entity types are present, and where the gaps are.

The Catalog you produce is the foundation for all subsequent phases.

Phase 0 runs in two tracks — run one, the other, or both in hybrid mode:

- **Track A (Schema-first)**: Systems and schema definitions are provided.
  Parse DDL, read API docs, or use playbook knowledge to document schema metadata.
  Output: `system_manifest.yaml`

- **Track B (File-based)**: A data room of exported files is provided.
  Profile files statistically, detect join keys, identify entity candidates.
  Output: `data_catalog.yaml`

- **Track C (Hybrid)**: Both inputs available. Run both tracks.
  Merge output into `data_catalog.yaml` with `system_manifest_ref`.

If you have both, prefer Track A for structural truth (FKs, cardinality, schema)
and Track B for statistical truth (actual distributions, value patterns, quality).

---

## Context Manifest

Load before starting:
- This file
- `schemas/system_manifest.yaml` (Track A)
- `schemas/data_catalog.yaml` (Track B / output)
- `data/{company}/engagement_brief.md`
- `playbooks/system_schemas/_index.md` (Track A — load specific skills as needed)
- `playbooks/data_formats/_index.md` (Track B — load specific skills as needed)

---

## Track A: Schema-First

Use when the engagement brief lists source systems with schema definitions
(DDL files, API docs) or system names to research. Operations A.1-A.3.

### A.1: Parse System Declarations

Read `data/{company}/engagement_brief.md` → `## Systems` section.
For each declared system, create an entry in `system_manifest.yaml`:

```yaml
- system_id: quickbooks          # slugified name
  name: QuickBooks Enterprise
  purpose: Accounting — GL, AP/AR, job costing, payroll
  vendor: Intuit
  schema_source: ddl_file        # ddl_file | api_docs | research | flat_files
  schema_path: schemas/quickbooks.sql   # relative to data room, or null
  schema_url: null
  schema_confidence: high        # high | medium | low
```

`schema_source` determines the next step for each system.

### A.2: Build Schema Metadata

For each system, populate `tables` (database systems) or `endpoints` (API systems):

**DDL file** (`schema_source: ddl_file`):
Run `tools/parse_ddl.py`:
```bash
python tools/parse_ddl.py data/{company}/schemas/system.sql \
  --output runs/{run_id}/phase_0_catalog/schemas/{system_id}.yaml
```
Import the parsed output into the system's `tables` entry in `system_manifest.yaml`.
`schema_confidence: high`.

**API docs** (`schema_source: api_docs`):
Read the API documentation (URL in `schema_url`). Extract:
- Endpoint paths and methods
- Object types returned
- Fields with types and required flags
- Any cross-resource references (FK equivalents)

Populate the system's `endpoints` entry. `schema_confidence: high`.

**Research** (`schema_source: research`):
Load the appropriate playbook from `playbooks/system_schemas/`:
- Accounting system → `accounting_erp.md`
- Project management → `project_management.md`
- HRIS / payroll → `hris_payroll.md`
- CRM → `crm.md`

Document the known schema from playbook knowledge. Set `schema_confidence: medium`.
Add note: "Schema from playbook knowledge — verify against actual system before mapping."

**Unknown system** (`schema_source: research`, system not in playbooks):
Document what can be inferred from the system name and purpose. List expected
tables/objects as best guesses. Set `schema_confidence: low`.

### A.3: Detect Cross-System Relationships

After all systems are documented, find relationships across them:

1. **Declared FKs already captured**: If a DDL FK explicitly references
   another system's table (rare), record as `method: declared_fk`, `confidence: 1.0`.

2. **Name-based matching**: Look for columns that share a name pattern with
   primary key columns in other systems (e.g., `customer_id` in a project
   management system → Customer table in accounting system).
   Record as `method: name_match`, `confidence: 0.7`.

3. **Semantic matching**: Columns that conceptually reference another system's
   entities even without a direct name match (e.g., `contractor_number` likely
   references the AP vendor table in accounting).
   Record as `method: semantic_match`, `confidence: 0.5`.

Populate `cross_system_relationships` in `system_manifest.yaml`.

For each relationship, document:
- `from_system` / `from_table` / `from_field`
- `to_system` / `to_table` / `to_field`
- `confidence`, `method`, `notes`

**Output**: `system_manifest.yaml` with all systems, schemas, and cross-system relationships

---

## Track B: File-Based

Use when the engagement brief references a data room of exported files.
This is the original Phase 0 path. Operations B.1-B.4.

### B.1: Walk the Data Room

Enumerate every file and directory in the data room. For every file:

- File path (relative to data room root)
- Format (csv, xlsx, pdf, json, txt, xml, sql, etc.)
- Size (bytes)
- For tabular files: note sheet names (Excel), apparent delimiter (CSV)
- For documents: note document type if obvious from name/path

A file you skip here is invisible to all downstream phases.

If the data room structure is unclear, load the relevant skill from
`playbooks/data_formats/` for guidance on recognizing formats.

**Output**: Initial `sources` list in `data_catalog.yaml` (path, format, size only)

### B.2: Profile Tabular Sources

Run `tools/profile_source.py` on every tabular file (CSV, Excel, TSV):
```bash
python tools/profile_source.py data/{company}/raw/file.csv \
  --output runs/{run_id}/phase_0_catalog/source_profiles/file_profile.yaml
```

The tool produces per-source statistical profiles:

- Column names, inferred types, null rates, cardinality
- Whether each column is a candidate key (high cardinality + unique)
- Whether each column is a candidate foreign key (matches another source's values)
- Row count, apparent grain, date range
- Sample values for each column

For each Excel file with multiple sheets, profile each sheet separately.

**Output**: `source_profiles/` directory + enriched `sources` list with column details

### B.3: Detect Join Keys

Run `tools/detect_joins.py` on the collected source profiles:
```bash
python tools/detect_joins.py runs/{run_id}/phase_0_catalog/source_profiles/ \
  --min-overlap 0.3
```

The tool produces a cross-source join-key candidate matrix:
- For every pair of columns across sources, check value overlap
- Report overlap rate and confidence score
- Flag high-confidence matches (overlap > 0.8, low null rate in both)

**Output**: `join_candidates` section of `data_catalog.yaml`

### B.4: Identify Candidate Entity Types

From the source profiles and join candidates, identify what entity types
exist in the data. For each candidate:

- **Name**: What is this thing? (Person, Contract, Department, etc.)
- **Sources**: Which files contain instances?
- **Instance count**: Approximately how many?
- **Identifier pattern**: How are instances identified? (ID column, name, code)

Heuristics (see `playbooks/entity_recognition/`):
- A column with high cardinality and unique values often represents entity IDs
- Column names containing "id", "code", "number" often reference entities
- The grain of a source implies an entity type
- Join candidates connect entity types across sources

Don't finalize entity types — that's Phase 1. Identify candidates and
note ambiguities ("Is this a person or a role?").

**Output**: `candidate_entity_types` section of `data_catalog.yaml`

---

## Both Tracks: Document Gaps

After completing Track A and/or Track B, document gaps and quality issues.

**Track A gaps:**
- Systems declared but no schema available (schema_confidence: low)
- Systems expected but not declared in the brief
- Cross-system relationships that are semantic guesses only (confidence < 0.7)
- Tables or endpoints missing grain, description, or candidate_entity_types

**Track B gaps:**
- Expected source files that don't exist
- High null rates, inconsistent formats, duplicate keys, encoding problems
- Cross-reference failures (low join overlap where high overlap expected)
- Ambiguous grain (unclear what one row represents)
- Temporal gaps (date ranges that don't cover the expected period)

Rate each gap by severity:
- **Critical**: Blocks a core entity type or relationship from being mapped
- **Significant**: Reduces confidence in a major part of the ontology
- **Minor**: Inconvenience or incompleteness that can be worked around

**Output**: `gaps` section of `data_catalog.yaml`

---

## Self-Validation

Before proceeding to Phase 1, verify:

**Track A:**
1. Every system from the engagement brief has an entry in `system_manifest.yaml`
2. Every system has `schema_confidence` set
3. Every table has `candidate_entity_types` populated
4. Cross-system relationships documented with confidence scores
5. System manifest conforms to `schemas/system_manifest.yaml`

**Track B:**
1. Every file in the data room appears in `data_catalog.yaml`
2. Every tabular source has a statistical profile in `source_profiles/`
3. Join candidates have been computed with confidence scores
4. At least one candidate entity type has been identified
5. `data_catalog.yaml` conforms to `schemas/data_catalog.yaml`

Run `tools/validate_catalog.py` to check Track B items 1, 2, and 5 automatically.

---

## What NOT to Do

- Don't build the ontology yet — just identify candidates
- Don't map fields to properties — just profile what exists
- Don't design pipelines — just inventory formats and schemas
- Don't skip Track A FK relationships — they're confidence=1.0 and inform
  Phase 1 more reliably than any file-based join detection
- Don't skip document files in Track B — they may contain entity references
  and relationship evidence even if they aren't tabular
