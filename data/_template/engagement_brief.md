# Engagement Brief — {Company Name}

## Company

- **Name:** {Company Name}
- **Industry:** {Industry / sector}
- **Size:** {Revenue, headcount, or other scale indicator}
- **Situation:** {Brief context — why are we looking at this company?}

## Systems

{Declare each source system. This drives Phase 0 Track A (schema-first).
Provide as much as you have — DDL file, API docs URL, or just the system name.
Unknown systems can be researched from playbook knowledge.}

| System | Vendor | Purpose | Schema Source | Schema Path / URL |
|--------|--------|---------|---------------|------------------|
| {e.g., QuickBooks Enterprise} | Intuit | Accounting — GL, AP/AR, job costing | ddl_file | schemas/quickbooks.sql |
| {e.g., Procore} | Procore | Construction project management | api_docs | https://developers.procore.com/reference |
| {e.g., ADP Workforce Now} | ADP | Payroll, HR, benefits | research | — |
| {e.g., Monday.com} | Monday.com | Project tracking | research | — |

**Schema Source values:**
- `ddl_file` — SQL DDL file in the data room schemas/ directory
- `api_docs` — Official API documentation (URL required)
- `research` — Known system; schema from playbook knowledge
- `flat_files` — No schema; only flat file exports (falls back to Track B)

## Data Room

{Leave blank if doing schema-only (Track A). Required for Track B (file-based profiling).}

- **Path:** {Absolute path to the raw data directory, or "none"}
- **Structure:** {Description — organized by system, flat dump, mixed, etc.}
- **Received:** {Date data was received}

{If the data room contains exports from known systems, note which system
each directory or file set came from — context for Track B profiling:}

- {e.g., SAP (ERP) — GL exports, vendor master}
- {e.g., Salesforce (CRM) — customer records, opportunities}
- {e.g., Workday (HRIS) — employee records, org structure}
- {e.g., SharePoint — board decks, memos, strategy documents}

## Expected Entity Types

{List entity types you expect to find, if known. The ontology
discovery process will confirm or reject these and find others.}

- {e.g., Employees, Departments, Customers, Contracts}

## Special Concerns

{Anything that should influence the ontology or mapping:}

- {e.g., Company recently merged two divisions — org data may be inconsistent}
- {e.g., Contract data is split across legal and finance systems}
- {e.g., Need behavioral/communication data for Simulation consumption}

## Prior Work

{Reference to DayZero assessment or other prior analysis, if any.}

- **DayZero run:** {path or "none"}
- **SDG output:** {path or "none"}

## Scope

{Any limitations on what should be included or excluded.}
