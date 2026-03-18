# Ontograph

Ontograph discovers the ontology, data mapping, and ETL architecture for a new
company's data. Given a raw data room (any structure, any format), it produces:

1. **Data Catalog** — inventory and statistical profile of every source
2. **Ontology** — entity types, relationship types, properties, domain concepts
3. **Mapping Plan** — how raw sources map to the ontology, including computed fields
4. **ETL Architecture** — pipeline design for Neo4j graph population

## Quick Start

1. Create an engagement brief: `data/{company}/engagement_brief.md`
2. Point `raw/` to the data room (symlink or path)
3. Read `INDEX.md` for the phase DAG and output contracts
4. Execute phases in order: Catalog → Ontology → Mapping → Architecture → Deliver

## Phase DAG

```
Catalog → Ontology → Mapping → Architecture → Deliver
  │          │          │           │             │
  │          │          │           │             └─ Human-readable documents
  │          │          │           └─ ETL specs + Neo4j schema
  │          │          └─ Source-to-ontology field mappings
  │          └─ Entity types, relationships, domain concepts
  └─ Data inventory + statistical profiles
```

## Key Documents

| Doc | Purpose |
|-----|---------|
| `INDEX.md` | Phase DAG, output contracts, run structure |
| `CLAUDE.md` | Agent operating instructions |
| `phases/*.md` | Phase-by-phase instructions |
| `schemas/*.yaml` | Output contract definitions |
| `playbooks/` | Domain expertise for data recognition |
| `tools/` | Deterministic Python tools |
