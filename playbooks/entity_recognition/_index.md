# Entity Recognition — Playbook Index

Heuristics and patterns for identifying entity types from data signals.
Use during Phase 1 (Ontology Discovery) when evaluating candidate entity
types from the Phase 0 catalog.

## When to Load

Load specific skills when you encounter data in a particular domain and
need guidance on what entity types to look for and how to distinguish
entities from properties.

## Skills

| Skill | Domain | Key Entity Types |
|-------|--------|-----------------|
| `people_organizations.md` | HR, org structure | Person, Department, Role, Team |
| `financial_entities.md` | Finance, accounting | Account, CostCenter, RevenueSegment, Budget |
| `contracts_agreements.md` | Legal, procurement | Contract, Provision, Counterparty, Term |
| `operations_systems.md` | IT, operations | Initiative, System, Process, Asset |
| `temporal_entities.md` | Planning, reporting | Period, Event, Milestone, Timeline |

## The Core Heuristic

Something is an **entity type** (not a property) when it satisfies 2+ of:

1. **Own lifecycle**: Created, modified, terminated independently
2. **Multiple relationships**: Participates in relationships with 2+ other types
3. **Referenced by others**: Multiple other things point to it
4. **Own properties**: Has attributes beyond the context where it appears

## Routing

- **Employee/staffing data?** → Load `people_organizations.md`
- **GL, P&L, balance sheet data?** → Load `financial_entities.md`
- **Customer/vendor/legal data?** → Load `contracts_agreements.md`
- **Project/system/process data?** → Load `operations_systems.md`
- **Timeline/schedule/milestone data?** → Load `temporal_entities.md`
