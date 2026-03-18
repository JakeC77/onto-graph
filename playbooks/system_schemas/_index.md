# System Schemas — Playbook Index

Known schema patterns for common business software systems.
Use during Phase 0 Track A when `schema_source: research` — the system name
is known but no DDL or API docs were provided.

## When to Load

Load specific skills when you need to document a system's schema from
knowledge rather than a provided DDL file. The skill gives you:
- Core tables or API objects for the system
- Key foreign key relationships
- Common gotchas and naming conventions
- Candidate entity types per table

These are starting points — always note `schema_confidence: medium` and
document any deviations found during engagement.

## Skills

| Skill | Systems Covered |
|-------|----------------|
| `accounting_erp.md` | QuickBooks, Sage 100/300, Xero, NetSuite |
| `project_management.md` | Procore, Buildertrend, Monday.com, Smartsheet |
| `hris_payroll.md` | ADP Workforce Now, Gusto, Workday, BambooHR |
| `crm.md` | Salesforce, HubSpot, Pipedrive |

## Routing

- **Accounting / GL / AP / AR / payroll?** → Load `accounting_erp.md`
- **Project tracking / job costing / construction?** → Load `project_management.md`
- **HR / headcount / benefits / payroll processing?** → Load `hris_payroll.md`
- **Sales / pipeline / customer records?** → Load `crm.md`
- **Unknown or niche system?** → Document tables as `UNKNOWN`, note gaps,
  set `schema_confidence: low`

## Output

After loading a skill and documenting the system, populate the system's
entry in `system_manifest.yaml` with:
- `schema_source: research`
- `schema_confidence: medium`
- `tables` section populated from playbook knowledge
- A note in the system's `notes` field: "Schema from playbook knowledge —
  verify against actual system before mapping."
