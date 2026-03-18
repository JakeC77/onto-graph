# Phase 1: Ontology Discovery

Discover the entity types, relationships, properties, and domain concepts
for this company. By the end of this phase, you have a complete ontology
that reflects what's actually in the data — not what you assumed would be there.

Every entity type and relationship must trace to evidence in the source data.
Non-trivial judgments get decision records (D_1xxx).

## Context Manifest

Load before starting:
- This file
- `schemas/ontology.yaml`
- `schemas/decision.yaml`
- Phase 0 output: `{run}/phase_0_catalog/data_catalog.yaml` (Track B, if exists)
- Phase 0 system manifest: `{run}/phase_0_catalog/system_manifest.yaml` (Track A, if exists)
- Phase 0 profiles: `{run}/phase_0_catalog/source_profiles/` (Track B, if exists)
- `playbooks/entity_recognition/_index.md`
- `playbooks/relationship_inference/_index.md`

**Track A input note:** FK relationships in `system_manifest.yaml` derived from
DDL parsing are structural facts, not inferences. Treat them as:
- `discovery_method: declared_fk`
- `confidence: 1.0`
Cardinality is explicit from the schema (PK → FK is always 1:N or 1:1).
Do not re-derive these from file overlap — just record them.

---

## Operations

Five operations. All are agent-driven, grounded in Phase 0 catalog output.

### 1.1: Establish Entity Types

Start with candidate entity types from Phase 0.

**If Track A (schema-first):** Seed candidates from `system_manifest.yaml` →
each system's `tables[].candidate_entity_types` and `cross_system_relationships`.
Tables with many inbound FKs are strong hub entity candidates.
`candidate_entity_types` per table are playbook-derived starting points — confirm
or reject using the heuristics below.

**If Track B (file-based):** Seed from `data_catalog.yaml` →
`candidate_entity_types` from profiling and join detection.

For each candidate:

**Confirm or reject.** Apply the entity-type heuristics (load from
`playbooks/entity_recognition/`):

- Does it have its own lifecycle? (created, modified, terminated independently)
- Does it participate in multiple relationships?
- Would multiple other things reference it?
- Does it have properties of its own beyond the context where it appears?

If YES to 2+ of these → it's an entity type.
If NO to all → it's a property of another entity type.
If ambiguous → write a decision record (D_1xxx) with evidence and rationale.

**Define each confirmed entity type:**

- **Name**: PascalCase (Person, Department, CustomerContract)
- **Description**: One paragraph — what this represents in this company
- **Identifier**: Which property uniquely identifies instances, what pattern
- **Properties**: List with name, type, required/optional, source (direct/computed/inferred)
- **Lifecycle**: What states exist? Which field holds the state?
- **Sources**: Which source files contain instances (source_ids from catalog)
- **Instance count**: How many exist in the data
- **Evidence**: Specific source locations that demonstrate this entity type exists

Look beyond the obvious. Phase 0 may have missed entity types that:
- Are embedded in document content (not tabular)
- Are implicit (e.g., "approval" is an entity type if approvals have properties)
- Span multiple sources (e.g., "project" appears in both initiative tracking
  and financial data but under different names)

**Output**: `entity_types` section of `ontology.yaml`

### 1.2: Establish Relationship Types

For each pair of entity types, determine what relationships exist.

**Discovery methods** (load from `playbooks/relationship_inference/`):

1. **Declared FK** (Track A): DDL `FOREIGN KEY` constraint. `confidence: 1.0`.
   Cardinality is unambiguous — FK column side is "many", PK side is "one".
2. **Explicit FK** (Track B): Column in one source references another source's key
   (join candidates from Phase 0)
3. **Junction table**: A source exists whose purpose is to link two entity types
4. **Column reference**: A column in entity A's source contains entity B's identifier
5. **Co-occurrence**: Entities A and B appear in the same row, implying a relationship
6. **Document analysis**: Narrative content describes a relationship
7. **Inference**: Statistical or behavioral patterns suggest a relationship

**Processing order:** Process declared FKs first (they're structural truth).
Then process inferred relationships to fill gaps.

**Define each relationship:**

- **Name**: snake_case (reports_to, owns_contract, member_of)
- **From/To**: Which entity types it connects
- **Cardinality**: 1:1, 1:N, N:1, N:M
- **Required**: Must every from-instance have this relationship?
- **Properties**: Attributes on the relationship itself (e.g., start_date)
- **Discovery method**: How was this found?
- **Confidence**: 0.0-1.0 based on evidence strength
- **Evidence**: Specific source locations

Write decision records for:
- Ambiguous directionality (A→B or B→A?)
- Ambiguous cardinality (1:N or N:M?)
- Relationships discovered by inference (lower confidence)

**Output**: `relationship_types` section of `ontology.yaml`

### 1.3: Define Property Catalog

For each entity type, classify every property:

- **Direct properties**: Exist as columns in source data. Map 1:1.
- **Computed properties**: Derived from source data via calculation. Define the
  computation spec (inputs, formula). These become statistical specs in Phase 2.
- **Inferred properties**: Not in any source but needed by downstream consumers
  (especially Simulation). Document what would need to be inferred and from what.

For computed and inferred properties, be specific about:
- What input data is required
- What calculation or inference method applies
- What assumptions are embedded
- What confidence level is achievable

**Output**: Updated `properties` for each entity type in `ontology.yaml`

### 1.4: Define Domain Concepts

Capture company-specific vocabulary that gives the ontology semantic meaning:

- What does "active" mean for contracts? (signed and not expired? or executed?)
- What are the organizational levels? (VP, Director, Manager — what do they mean?)
- What are the revenue categories? (recurring, one-time, pass-through?)
- What status values exist for initiatives? (green/yellow/red? or phase-based?)

For each domain concept:
- **Name**: The term as used in this company
- **Definition**: What it means in this context
- **Entity type**: Where it applies
- **Values**: Enumerated if applicable
- **Source**: Where in the data this concept appears

Domain concepts are critical for Phase 2 (mapping) because they define
how raw values should be interpreted and transformed.

**Output**: `domain_concepts` section of `ontology.yaml`

### 1.5: Simulation Compatibility Check

Compare the discovered ontology against Simulation's graph contract.

**Simulation's expected node types:**
Person, Department, Initiative, System, Process, CustomerContract,
VendorContract, Customer, Covenant

**Simulation's expected edge types:**
reports_to, member_of, works_on, manages, owns_initiative, owns_contract,
owns_system, approves, uses_system, cost_dependency, trust, communicates,
influence

For each:
- **Match**: Ontology type maps directly to Simulation type
- **Mappable**: Ontology type is similar but named differently or structured differently
- **Unmapped**: Ontology type has no Simulation equivalent (may need extension)
- **Missing**: Simulation expects this type but data doesn't support it

This is informational — the ontology reflects the data, not Simulation's needs.
But gaps should be visible early.

**Output**: `simulation_compatibility` section of `ontology.yaml`

---

## Self-Validation

Before proceeding to Phase 2, verify:

1. Every entity type has at least one source file with instances
2. Every entity type has at least one relationship
3. Every relationship type has evidence from at least one source
4. No orphan entity types (types with no relationships)
5. Decision records exist for all non-trivial judgments
6. Simulation compatibility matrix is complete
7. `ontology.yaml` conforms to `schemas/ontology.yaml`

Run `tools/validate_ontology.py` for automated consistency checks.
Run `tools/validate_evidence.py` for evidence chain verification.

---

## What NOT to Do

- Don't assume entity types from templates or domain knowledge — discover them
- Don't define relationships without evidence in the data
- Don't skip ambiguous cases — write decision records
- Don't optimize for Simulation compatibility — reflect the data
- Don't define computed properties without specifying the computation
