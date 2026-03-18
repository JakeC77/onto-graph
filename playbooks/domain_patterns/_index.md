# Domain Patterns — Playbook Index

Industry-specific ontology patterns that prime entity and relationship
recognition. These are recognition aids, NOT prescriptions. The ontology
is always discovered from the data.

## When to Load

Load the relevant domain skill during Phase 1 when you know the company's
industry (from the engagement brief or Phase 0 context). Use it to:
- Know what entity types to look for beyond the obvious
- Recognize domain-specific relationship patterns
- Understand domain vocabulary that may appear in column names

## Skills

| Skill | Industry | Key Patterns |
|-------|----------|-------------|
| `professional_services.md` | Consulting, law, staffing | Utilization, billing, matters, engagements |
| `software_saas.md` | SaaS, tech companies | ARR, churn, subscriptions, product usage |
| `manufacturing.md` | Manufacturing, distribution | BOM, routing, work orders, inventory |
| `financial_services.md` | Banks, PE, insurance | Portfolio, instruments, risk, compliance |
| `healthcare.md` | Healthcare, pharma, biotech | Patients, claims, formulary, trials |

## Usage Rule

These playbooks tell you what MIGHT exist, not what DOES exist. Every entity
type and relationship suggested by a domain pattern must still be confirmed
with evidence in the actual data. Do not add entity types just because the
domain pattern says they're common.
