# Phase 2: Data Mapping Plan

Define how every raw data source maps to the ontology. By the end of this
phase, for every property and relationship in the ontology, you know exactly
where the data comes from and what transformations apply.

This is the "what goes where" specification. It does NOT describe how to
build the pipeline — that's Phase 3.

## Context Manifest

Load before starting:
- This file
- `schemas/mapping_plan.yaml`
- `schemas/decision.yaml`
- Phase 0 output: `{run}/phase_0_catalog/data_catalog.yaml` (Track B, if exists)
- Phase 0 system manifest: `{run}/phase_0_catalog/system_manifest.yaml` (Track A, if exists)
- Phase 0 profiles: `{run}/phase_0_catalog/source_profiles/` (Track B, if exists)
- Phase 1 output: `{run}/phase_1_ontology/ontology.yaml`

**Source reference format:**
- Track A (schema-first): use `{system_id}.{table_name}.{column_name}`
  e.g., `quickbooks.Invoice.CustomerRef`
- Track B (file-based): use `{source_id}.{column_name}`
  e.g., `invoices_export.customer_id`
- Hybrid: use the Track A reference where DDL exists; Track B reference for
  files without a declared schema.

---

## Operations

Five operations. Grounded in the ontology (Phase 1) and catalog (Phase 0).

### 2.1: Source-to-Entity Mapping

For each entity type in the ontology, establish:

- **System of record**: Which source system (Track A) or source file (Track B)
  is the primary/authoritative source?
  Decision criteria: most complete, most recent, most frequently updated.
  For Track A: prefer the system where the entity is the native object
  (e.g., Person SOR = HRIS, Customer SOR = CRM).
- **Additional sources**: What supplementary sources contain this entity type?
- **Merge key**: Which property deduplicates instances across sources?
  (From Phase 0 join candidates.)
- **Conflict resolution**: When sources disagree on a value, which wins?
  Options: last_write_wins, source_priority (ranked list), manual.

Write a decision record (D_2xxx) for any non-obvious system-of-record choice
or conflict resolution strategy.

**Output**: `entity_mappings` section of `mapping_plan.yaml`

### 2.2: Field-Level Mapping

For each property of each entity type, specify:

- **Source**: Which source file and which column
- **Transformation**: What happens to the value?
  - `none` — direct copy
  - `cast` — type conversion (string → date, string → integer)
  - `normalize` — standardize format (trim whitespace, title case, etc.)
  - `lookup` — map coded values to labels (or vice versa)
  - `calculate` — derive from other fields (see 2.4 for complex calculations)
  - `concat` — combine multiple source fields
  - `split` — extract part of a source field
  - `conditional` — value depends on a condition
- **Transformation spec**: Details (e.g., "parse as YYYY-MM-DD", "lookup from department_codes.csv")
- **Null handling**: What to do when the source value is missing
  - `default` — use a specified default value
  - `skip` — leave the property empty
  - `flag` — populate but mark as incomplete
- **Validation**: Expected type, valid range, referential integrity

Be specific. "Transform the date" is not a mapping. "Parse column 'hire_date'
as ISO-8601 date, default to null if unparseable" is a mapping.

**Output**: `field_mappings` within each entity mapping in `mapping_plan.yaml`

### 2.3: Relationship Extraction Mapping

For each relationship type in the ontology, specify how to extract it:

- **declared_fk** (Track A only): Relationship is a DDL FK constraint.
  Specify: `{system}.{table}.{fk_column}` → `{system}.{table}.{pk_column}`.
  These get `confidence: 1.0` automatically from Phase 1.
- **fk_lookup**: Source column directly references another entity's ID.
  Specify: source file, from-field, to-field.
- **junction_table**: A dedicated table links two entity types.
  Specify: junction source, from-field, to-field, any relationship properties.
- **co_occurrence**: Entities appear together in the same row.
  Specify: source file, how each entity is identified in the row.
- **computation**: Relationship must be computed (e.g., "collaborates_with"
  from communication frequency).
  Specify: input data, computation method, threshold.
- **document_parse**: Relationship described in narrative text.
  Specify: document source, extraction method, confidence.

For each relationship property (e.g., start_date on "reports_to"), include
a field-level mapping like 2.2.

**Output**: `relationship_mappings` section of `mapping_plan.yaml`

### 2.4: Statistical Computation Specifications

For properties marked as `computed` or `inferred` in the ontology, define
the full computation:

- **Name**: Descriptive name (e.g., "workload_capacity")
- **Target**: Which entity type and property this produces
- **Inputs**: Source files, fields, and any aggregation applied
  (sum, avg, count, max, min, distinct_count)
- **Window**: Time window for aggregation (30d, quarterly, trailing_12m)
- **Formula**: Human-readable calculation
- **Output type**: Data type of the result

Examples:
- `workload_capacity = count(active_initiatives) * avg(hours_per_initiative) / available_hours`
- `communication_density = count(emails_30d) / count(distinct_recipients_30d)`
- `approval_authority = sum(approved_value_90d) / count(approval_requests_90d)`

Verify each computation is feasible: do the input fields exist in the data?
If not, document the gap.

**Output**: `statistical_computations` section of `mapping_plan.yaml`

### 2.5: Coverage Attestation

Verify completeness:

1. **Property coverage**: Every property in the ontology has a field mapping
   (or a documented gap with reason and downstream impact).
2. **Source utilization**: Every source file is consumed by at least one
   mapping (or explicitly excluded with a reason).
3. **No circular dependencies**: Computed fields don't reference other
   computed fields in a cycle.
4. **Statistical feasibility**: Every computation spec is computable
   from available data.

Compute coverage rate = mapped_properties / total_properties.

**Output**: `coverage` and `source_utilization` sections of `mapping_plan.yaml`

---

## Self-Validation

Before proceeding to Phase 3, verify:

1. 100% property coverage (every property mapped or gap-documented)
2. 100% source utilization (every source consumed or excluded with reason)
3. No circular computed-field dependencies
4. All statistical specs reference existing source fields
5. Decision records for non-obvious choices
6. `mapping_plan.yaml` conforms to `schemas/mapping_plan.yaml`

Run `tools/validate_mapping.py` for automated checks.

---

## What NOT to Do

- Don't design the ETL pipeline — just specify what maps where
- Don't write actual transformation code — just describe the transformation
- Don't assume data quality — if a mapping depends on clean data, note the assumption
- Don't skip gap documentation — a gap is better than a wrong mapping
