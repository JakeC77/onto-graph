# Engagement Brief — Ridgeline Builders

## Company

- **Name:** Ridgeline Builders
- **Industry:** Residential & light commercial general contracting
- **Size:** ~$1.4M (2024) → ~$1.9M (2025) revenue, 5-9 employees
- **Situation:** BOH agent development target. Using generated demo data to
  build the ontology and graph schema that will power an OpenClaw-based
  back-of-house assistant for small builders.

## Systems

| System | Vendor | Purpose | Schema Source | Schema Path / URL |
|--------|--------|---------|---------------|------------------|
| Builder Data Generator | Internal | Full operational dataset — projects, estimates, invoices, time, bills | flat_files | data_room/ |

**Schema Source values:**
- `flat_files` — CSV exports from the data generator. No DDL; schema discovered from file profiling (Track B).

## Data Room

- **Path:** data/ridgeline_builders/data_room/
- **Structure:** Flat directory of CSV files + JSON + SQLite, one file per entity type
- **Received:** 2026-03-18 (generated)

Files present:
- company.csv — Company master record
- customer.csv — Customer records
- vendor.csv — Vendor/subcontractor records
- employee.csv — Crew roster with roles and rates
- estimate.csv — Estimates (won and lost)
- estimate_line_item.csv — Estimate line items by cost code
- project.csv — Active/completed projects
- job.csv — Jobs (cost codes) within projects
- time_entry.csv — Crew time entries against jobs
- bill.csv — Vendor/sub bills
- bill_line_item.csv — Bill line items
- invoice.csv — Customer invoices
- payment.csv — Customer payments
- loc_event.csv — Line-of-credit draw events
- overtime_event.csv — Overtime narrative events
- pricing_change.csv — Material pricing change events
- data.json — All entities in single JSON file
- builder.db — SQLite database with all tables

## Expected Entity Types

- Company
- Customer
- Vendor (suppliers + subcontractors)
- Employee
- Estimate
- Project
- Job (cost code within a project)
- TimeEntry
- Bill / BillLineItem
- Invoice
- Payment
- ChangeOrder

## Special Concerns

- Data is generated, not from a live system. All records are internally consistent.
- Narrative events (late payments, cost overruns, crew changes) are baked into the
  data — the ontology should capture these patterns, not just static entities.
- The ultimate consumer of this ontology is an OpenClaw agent that needs to answer
  operational questions (scheduling, job costing, cash flow, estimating).
- Vendor records include both material suppliers and trade subcontractors — the
  ontology should distinguish these.

## Prior Work

- **DayZero run:** none
- **SDG output:** none

## Scope

Full operational dataset. All entity types and relationships should be discovered.
No exclusions.
