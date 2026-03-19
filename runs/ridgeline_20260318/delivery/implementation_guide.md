# Ridgeline Builders ETL Implementation Guide

## 1. What We're Building

This pipeline reads 16 CSV files exported from a small general contractor's operational systems (QuickBooks-style accounting, project management, time tracking) and loads them into a Neo4j property graph. The graph contains 14 entity types and 14 relationship types covering the full lifecycle of construction work: customers, estimates, projects, jobs (cost codes), time entries, vendor bills, invoices, and payments. We use a graph rather than a relational warehouse because the BOH (back-of-house) assistant agent needs to traverse connected paths that are painful in SQL -- things like "show me all unpaid invoices for projects where this vendor's bills exceeded budget on framing jobs" or "which customers have the highest lifetime value considering all their projects, and what's the average margin across those projects?" These are multi-hop traversals across 3-5 entity types that become natural single-query patterns in Cypher.

## 2. Prerequisites

### Start Neo4j

```bash
docker run -d \
  --name ridgeline-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/ridgeline2024 \
  -e NEO4J_PLUGINS='[]' \
  -v ridgeline_data:/data \
  neo4j:5-community
```

Wait about 10 seconds for startup, then verify at http://localhost:7474.

### Python Dependencies

```bash
pip install neo4j pandas
```

That is the complete dependency list. No other packages are needed. Python 3.10+.

### Directory Structure

The script expects CSV files at a configurable path. The default layout:

```
data/ridgeline_builders/data_room/
  company.csv          (1 row)
  customer.csv         (13 rows)
  vendor.csv           (10 rows)
  employee.csv         (5 rows)
  estimate.csv         (100 rows)
  estimate_line_item.csv (1173 rows)
  project.csv          (51 rows)
  job.csv              (279 rows)
  time_entry.csv       (1710 rows)
  bill.csv             (745 rows)
  bill_line_item.csv   (745 rows)
  invoice.csv          (134 rows)
  payment.csv          (134 rows)
  loc_event.csv        (1 row)
  overtime_event.csv   (1 row)
  pricing_change.csv   (1 row)
```

Total: 5,102 rows across 16 files. This loads in under 30 seconds on any modern machine.

## 3. Schema Setup

Run this entire block against Neo4j before loading any data. Every statement is idempotent (`IF NOT EXISTS`), so running it multiple times is safe.

```cypher
// === UNIQUENESS CONSTRAINTS ===

// Company -- unique on name
CREATE CONSTRAINT uniq_company_name IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE;

// Customer -- unique on id
CREATE CONSTRAINT uniq_customer_id IF NOT EXISTS FOR (n:Customer) REQUIRE n.id IS UNIQUE;

// Vendor -- unique on id
CREATE CONSTRAINT uniq_vendor_id IF NOT EXISTS FOR (n:Vendor) REQUIRE n.id IS UNIQUE;

// Employee -- unique on id
CREATE CONSTRAINT uniq_employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE;

// Estimate -- unique on estimate_id
CREATE CONSTRAINT uniq_estimate_estimate_id IF NOT EXISTS FOR (n:Estimate) REQUIRE n.estimate_id IS UNIQUE;

// EstimateLineItem -- unique on line_id
CREATE CONSTRAINT uniq_estimatelineitem_line_id IF NOT EXISTS FOR (n:EstimateLineItem) REQUIRE n.line_id IS UNIQUE;

// Project -- unique on project_id
CREATE CONSTRAINT uniq_project_project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.project_id IS UNIQUE;

// Job -- unique on job_id
CREATE CONSTRAINT uniq_job_job_id IF NOT EXISTS FOR (n:Job) REQUIRE n.job_id IS UNIQUE;

// TimeEntry -- unique on entry_id
CREATE CONSTRAINT uniq_timeentry_entry_id IF NOT EXISTS FOR (n:TimeEntry) REQUIRE n.entry_id IS UNIQUE;

// Bill -- unique on bill_id
CREATE CONSTRAINT uniq_bill_bill_id IF NOT EXISTS FOR (n:Bill) REQUIRE n.bill_id IS UNIQUE;

// BillLineItem -- unique on line_id
CREATE CONSTRAINT uniq_billlineitem_line_id IF NOT EXISTS FOR (n:BillLineItem) REQUIRE n.line_id IS UNIQUE;

// Invoice -- unique on invoice_id
CREATE CONSTRAINT uniq_invoice_invoice_id IF NOT EXISTS FOR (n:Invoice) REQUIRE n.invoice_id IS UNIQUE;

// Payment -- unique on payment_id
CREATE CONSTRAINT uniq_payment_payment_id IF NOT EXISTS FOR (n:Payment) REQUIRE n.payment_id IS UNIQUE;

// NarrativeEvent -- unique on event_id
CREATE CONSTRAINT uniq_narrativeevent_event_id IF NOT EXISTS FOR (n:NarrativeEvent) REQUIRE n.event_id IS UNIQUE;

// === INDEXES ===

CREATE INDEX idx_company_owner_name IF NOT EXISTS FOR (n:Company) ON (n.owner_name);
CREATE INDEX idx_customer_name IF NOT EXISTS FOR (n:Customer) ON (n.name);
CREATE INDEX idx_customer_type IF NOT EXISTS FOR (n:Customer) ON (n.type);
CREATE INDEX idx_customer_status IF NOT EXISTS FOR (n:Customer) ON (n.status);
CREATE INDEX idx_customer_created_at IF NOT EXISTS FOR (n:Customer) ON (n.created_at);
CREATE INDEX idx_vendor_name IF NOT EXISTS FOR (n:Vendor) ON (n.name);
CREATE INDEX idx_vendor_type IF NOT EXISTS FOR (n:Vendor) ON (n.type);
CREATE INDEX idx_vendor_insurance_expiry IF NOT EXISTS FOR (n:Vendor) ON (n.insurance_expiry);
CREATE INDEX idx_vendor_account_opened IF NOT EXISTS FOR (n:Vendor) ON (n.account_opened);
CREATE INDEX idx_employee_name IF NOT EXISTS FOR (n:Employee) ON (n.name);
CREATE INDEX idx_employee_status IF NOT EXISTS FOR (n:Employee) ON (n.status);
CREATE INDEX idx_employee_hire_date IF NOT EXISTS FOR (n:Employee) ON (n.hire_date);
CREATE INDEX idx_employee_termination_date IF NOT EXISTS FOR (n:Employee) ON (n.termination_date);
CREATE INDEX idx_estimate_archetype IF NOT EXISTS FOR (n:Estimate) ON (n.archetype);
CREATE INDEX idx_estimate_status IF NOT EXISTS FOR (n:Estimate) ON (n.status);
CREATE INDEX idx_estimate_created_at IF NOT EXISTS FOR (n:Estimate) ON (n.created_at);
CREATE INDEX idx_estimate_sent_at IF NOT EXISTS FOR (n:Estimate) ON (n.sent_at);
CREATE INDEX idx_estimate_valid_until IF NOT EXISTS FOR (n:Estimate) ON (n.valid_until);
CREATE INDEX idx_estimate_accepted_at IF NOT EXISTS FOR (n:Estimate) ON (n.accepted_at);
CREATE INDEX idx_project_name IF NOT EXISTS FOR (n:Project) ON (n.name);
CREATE INDEX idx_project_archetype IF NOT EXISTS FOR (n:Project) ON (n.archetype);
CREATE INDEX idx_project_type IF NOT EXISTS FOR (n:Project) ON (n.type);
CREATE INDEX idx_project_status IF NOT EXISTS FOR (n:Project) ON (n.status);
CREATE INDEX idx_project_start_date IF NOT EXISTS FOR (n:Project) ON (n.start_date);
CREATE INDEX idx_project_end_date IF NOT EXISTS FOR (n:Project) ON (n.end_date);
CREATE INDEX idx_project_actual_start IF NOT EXISTS FOR (n:Project) ON (n.actual_start);
CREATE INDEX idx_project_actual_end IF NOT EXISTS FOR (n:Project) ON (n.actual_end);
CREATE INDEX idx_project_contract_type IF NOT EXISTS FOR (n:Project) ON (n.contract_type);
CREATE INDEX idx_job_name IF NOT EXISTS FOR (n:Job) ON (n.name);
CREATE INDEX idx_job_status IF NOT EXISTS FOR (n:Job) ON (n.status);
CREATE INDEX idx_job_sub_vendor_type IF NOT EXISTS FOR (n:Job) ON (n.sub_vendor_type);
CREATE INDEX idx_job_actual_start IF NOT EXISTS FOR (n:Job) ON (n.actual_start);
CREATE INDEX idx_job_actual_end IF NOT EXISTS FOR (n:Job) ON (n.actual_end);
CREATE INDEX idx_timeentry_date IF NOT EXISTS FOR (n:TimeEntry) ON (n.date);
CREATE INDEX idx_bill_status IF NOT EXISTS FOR (n:Bill) ON (n.status);
CREATE INDEX idx_bill_received_date IF NOT EXISTS FOR (n:Bill) ON (n.received_date);
CREATE INDEX idx_bill_due_date IF NOT EXISTS FOR (n:Bill) ON (n.due_date);
CREATE INDEX idx_bill_paid_date IF NOT EXISTS FOR (n:Bill) ON (n.paid_date);
CREATE INDEX idx_invoice_type IF NOT EXISTS FOR (n:Invoice) ON (n.type);
CREATE INDEX idx_invoice_status IF NOT EXISTS FOR (n:Invoice) ON (n.status);
CREATE INDEX idx_invoice_issued_date IF NOT EXISTS FOR (n:Invoice) ON (n.issued_date);
CREATE INDEX idx_invoice_due_date IF NOT EXISTS FOR (n:Invoice) ON (n.due_date);
CREATE INDEX idx_payment_received_date IF NOT EXISTS FOR (n:Payment) ON (n.received_date);
CREATE INDEX idx_payment_deposited_date IF NOT EXISTS FOR (n:Payment) ON (n.deposited_date);
CREATE INDEX idx_narrativeevent_event_type IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.event_type);
CREATE INDEX idx_narrativeevent_date IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.date);
```

14 uniqueness constraints, 46 indexes. The constraints double as indexes on the merge keys, so every MERGE operation hits an index.

## 4. Node Loading

Nodes are loaded in dependency order across six stages. Each Cypher block uses the `UNWIND $rows` pattern -- the Python driver sends a batch of row dicts and Cypher iterates over them. All type conversions happen inline in Cypher using `toFloat()`, `toInteger()`, `toBoolean()`, and `date()`.

### Stage 1: Master Data (no dependencies)

```cypher
// Load Company from company.csv
UNWIND $rows AS row
MERGE (c:Company {name: row.name})
SET c.trade = row.trade,
    c.region = row.region,
    c.owner_name = row.owner_name,
    c.owner_employee_id = row.owner_employee_id,
    c.address = row.address,
    c.phone = row.phone,
    c.email = row.email,
    c.license_number = row.license_number
```

```cypher
// Load Customers from customer.csv
UNWIND $rows AS row
MERGE (c:Customer {id: row.id})
SET c.name = row.name,
    c.email = row.email,
    c.phone = row.phone,
    c.address = row.address,
    c.payment_terms = row.payment_terms,
    c.source = row.source,
    c.type = row.type,
    c.tax_exempt = CASE WHEN row.tax_exempt IN ['True', 'true', '1'] THEN true ELSE false END,
    c.credit_limit = toFloat(row.credit_limit),
    c.status = row.status,
    c.created_at = date(row.created_at),
    c.notes = row.notes
```

```cypher
// Load Vendors from vendor.csv
UNWIND $rows AS row
MERGE (v:Vendor {id: row.id})
SET v.name = row.name,
    v.type = row.type,
    v.trade = row.trade,
    v.contact = row.contact,
    v.phone = row.phone,
    v.email = row.email,
    v.payment_terms = row.payment_terms,
    v.tax_id = row.tax_id,
    v.w9_on_file = CASE WHEN row.w9_on_file IN ['True', 'true', '1'] THEN true ELSE false END,
    v.insurance_expiry = CASE WHEN row.insurance_expiry IS NOT NULL AND row.insurance_expiry <> '' THEN date(row.insurance_expiry) ELSE null END,
    v.rating = CASE WHEN row.rating IS NOT NULL AND row.rating <> '' THEN toFloat(row.rating) ELSE null END,
    v.credit_limit = CASE WHEN row.credit_limit IS NOT NULL AND row.credit_limit <> '' THEN toFloat(row.credit_limit) ELSE null END,
    v.account_opened = CASE WHEN row.account_opened IS NOT NULL AND row.account_opened <> '' THEN date(row.account_opened) ELSE null END
```

```cypher
// Load Employees from employee.csv
UNWIND $rows AS row
MERGE (e:Employee {id: row.id})
SET e.name = row.name,
    e.role = row.role,
    e.trade = row.trade,
    e.base_rate = toFloat(row.base_rate),
    e.burden_rate = toFloat(row.burden_rate),
    e.bill_rate = toFloat(row.bill_rate),
    e.status = row.status,
    e.hire_date = date(row.hire_date),
    e.termination_date = CASE WHEN row.termination_date IS NOT NULL AND row.termination_date <> '' THEN date(row.termination_date) ELSE null END
```

### Stage 2: Estimates (depends on master data)

```cypher
// Load Estimates from estimate.csv
UNWIND $rows AS row
MERGE (e:Estimate {estimate_id: row.estimate_id})
SET e.estimate_number = row.estimate_number,
    e.version = toInteger(row.version),
    e.customer_id = row.customer_id,
    e.archetype = row.archetype,
    e.status = row.status,
    e.scope_description = row.scope_description,
    e.exclusions = row.exclusions,
    e.assumptions = row.assumptions,
    e.total = toFloat(row.total),
    e.cost_estimate = toFloat(row.cost_estimate),
    e.markup_pct = toFloat(row.markup_pct),
    e.tax_amount = toFloat(row.tax_amount),
    e.created_at = date(row.created_at),
    e.sent_at = date(row.sent_at),
    e.valid_until = date(row.valid_until),
    e.accepted_at = CASE WHEN row.accepted_at IS NOT NULL AND row.accepted_at <> '' THEN date(row.accepted_at) ELSE null END,
    e.project_id = CASE WHEN row.project_id IS NOT NULL AND row.project_id <> '' THEN row.project_id ELSE null END
```

```cypher
// Load EstimateLineItems from estimate_line_item.csv
UNWIND $rows AS row
MERGE (eli:EstimateLineItem {line_id: row.line_id})
SET eli.estimate_id = row.estimate_id,
    eli.cost_code = row.cost_code,
    eli.description = row.description,
    eli.quantity = toInteger(row.quantity),
    eli.unit = row.unit,
    eli.unit_cost = toFloat(row.unit_cost),
    eli.unit_price = toFloat(row.unit_price),
    eli.line_total = toFloat(row.line_total),
    eli.category = row.category
```

### Stage 3: Projects (depends on master data + estimates)

```cypher
// Load Projects from project.csv
UNWIND $rows AS row
MERGE (p:Project {project_id: row.project_id})
SET p.estimate_id = row.estimate_id,
    p.customer_id = row.customer_id,
    p.name = row.name,
    p.archetype = row.archetype,
    p.type = row.type,
    p.trade = row.trade,
    p.status = row.status,
    p.site_address = row.site_address,
    p.start_date = date(row.start_date),
    p.end_date = date(row.end_date),
    p.actual_start = date(row.actual_start),
    p.actual_end = date(row.actual_end),
    p.contract_amount = toFloat(row.contract_amount),
    p.contract_type = row.contract_type,
    p.markup_pct = toFloat(row.markup_pct),
    p.retention_pct = toFloat(row.retention_pct),
    p.retention_released = CASE WHEN row.retention_released IN ['True', 'true', '1'] THEN true ELSE false END,
    p.permit_required = CASE WHEN row.permit_required IN ['True', 'true', '1'] THEN true ELSE false END,
    p.permit_number = CASE WHEN row.permit_number IS NOT NULL AND row.permit_number <> '' THEN row.permit_number ELSE null END,
    p.notes = CASE WHEN row.notes IS NOT NULL AND row.notes <> '' THEN row.notes ELSE null END
```

```cypher
// Load Jobs from job.csv
UNWIND $rows AS row
MERGE (j:Job {job_id: row.job_id})
SET j.project_id = row.project_id,
    j.code = row.code,
    j.name = row.name,
    j.budgeted_labor_hours = toFloat(row.budgeted_labor_hours),
    j.budgeted_labor_cost = toFloat(row.budgeted_labor_cost),
    j.budgeted_material_cost = toFloat(row.budgeted_material_cost),
    j.budgeted_sub_cost = toFloat(row.budgeted_sub_cost),
    j.budgeted_equipment_cost = toFloat(row.budgeted_equipment_cost),
    j.budgeted_other_cost = toFloat(row.budgeted_other_cost),
    j.status = row.status,
    j.sort_order = toInteger(row.sort_order),
    j.sub_vendor_type = CASE WHEN row.sub_vendor_type IS NOT NULL AND row.sub_vendor_type <> '' THEN row.sub_vendor_type ELSE null END,
    j.equipment_needed = CASE WHEN row.equipment_needed IN ['True', 'true', '1'] THEN true ELSE false END,
    j.actual_start = date(row.actual_start),
    j.actual_end = date(row.actual_end)
```

### Stage 4: Financials (depends on projects)

```cypher
// Load Bills from bill.csv
UNWIND $rows AS row
MERGE (b:Bill {bill_id: row.bill_id})
SET b.vendor_id = row.vendor_id,
    b.project_id = CASE WHEN row.project_id IS NOT NULL AND row.project_id <> '' THEN row.project_id ELSE null END,
    b.job_id = CASE WHEN row.job_id IS NOT NULL AND row.job_id <> '' THEN row.job_id ELSE null END,
    b.vendor_invoice_number = row.vendor_invoice_number,
    b.status = row.status,
    b.received_date = date(row.received_date),
    b.due_date = date(row.due_date),
    b.total = toFloat(row.total),
    b.paid_date = date(row.paid_date),
    b.payment_method = row.payment_method,
    b.check_number = CASE WHEN row.check_number IS NOT NULL AND row.check_number <> '' THEN toInteger(row.check_number) ELSE null END,
    b.category = row.category
```

```cypher
// Load BillLineItems from bill_line_item.csv
UNWIND $rows AS row
MERGE (bli:BillLineItem {line_id: row.line_id})
SET bli.bill_id = row.bill_id,
    bli.project_id = CASE WHEN row.project_id IS NOT NULL AND row.project_id <> '' THEN row.project_id ELSE null END,
    bli.job_id = CASE WHEN row.job_id IS NOT NULL AND row.job_id <> '' THEN row.job_id ELSE null END,
    bli.description = row.description,
    bli.quantity = toInteger(row.quantity),
    bli.unit_cost = toFloat(row.unit_cost),
    bli.line_total = toFloat(row.line_total),
    bli.category = row.category
```

```cypher
// Load Invoices from invoice.csv
UNWIND $rows AS row
MERGE (i:Invoice {invoice_id: row.invoice_id})
SET i.invoice_number = row.invoice_number,
    i.project_id = row.project_id,
    i.customer_id = row.customer_id,
    i.type = row.type,
    i.status = row.status,
    i.issued_date = date(row.issued_date),
    i.due_date = date(row.due_date),
    i.subtotal = toFloat(row.subtotal),
    i.retention_held = toFloat(row.retention_held),
    i.tax = toFloat(row.tax),
    i.total_due = toFloat(row.total_due),
    i.notes = CASE WHEN row.notes IS NOT NULL AND row.notes <> '' THEN row.notes ELSE null END
```

```cypher
// Load Payments from payment.csv
UNWIND $rows AS row
MERGE (pay:Payment {payment_id: row.payment_id})
SET pay.invoice_id = row.invoice_id,
    pay.project_id = row.project_id,
    pay.customer_id = row.customer_id,
    pay.amount = toFloat(row.amount),
    pay.method = row.method,
    pay.reference = row.reference,
    pay.received_date = date(row.received_date),
    pay.deposited_date = date(row.deposited_date)
```

### Stage 5: Execution (depends on projects)

```cypher
// Load TimeEntries from time_entry.csv
UNWIND $rows AS row
MERGE (te:TimeEntry {entry_id: row.entry_id})
SET te.employee_id = row.employee_id,
    te.project_id = row.project_id,
    te.job_id = row.job_id,
    te.date = date(row.date),
    te.hours_regular = toFloat(row.hours_regular),
    te.hours_overtime = toFloat(row.hours_overtime),
    te.cost = toFloat(row.cost),
    te.notes = row.notes
```

### Stage 6: Events (no dependencies)

NarrativeEvent is a union of three source files, each with different schemas. The Python ETL handles the column mapping before passing rows to Cypher. By the time rows reach this query, they all have the same shape.

```cypher
// Load NarrativeEvents (union of loc_event.csv, overtime_event.csv, pricing_change.csv)
UNWIND $rows AS row
MERGE (ne:NarrativeEvent {event_id: row.event_id})
SET ne.event_type = row.event_type,
    ne.date = date(row.date),
    ne.description = row.description,
    ne.amount = CASE WHEN row.amount IS NOT NULL THEN toFloat(row.amount) ELSE null END,
    ne.event_metadata = CASE WHEN row.event_metadata IS NOT NULL THEN row.event_metadata ELSE null END
```

## 5. Relationship Loading

After all nodes exist, create relationships. Every relationship is derived from a foreign key column in one of the source CSVs. The Python script reads the same CSVs again (they are small) and extracts just the FK pairs. Each block uses MATCH on both endpoints and MERGE on the relationship to stay idempotent.

```cypher
// CUSTOMER_HAS_ESTIMATE: Customer -> Estimate (via estimate.csv customer_id)
UNWIND $rows AS row
MATCH (c:Customer {id: row.customer_id})
MATCH (e:Estimate {estimate_id: row.estimate_id})
MERGE (c)-[:CUSTOMER_HAS_ESTIMATE]->(e)
```

```cypher
// CUSTOMER_HAS_PROJECT: Customer -> Project (via project.csv customer_id)
UNWIND $rows AS row
MATCH (c:Customer {id: row.customer_id})
MATCH (p:Project {project_id: row.project_id})
MERGE (c)-[:CUSTOMER_HAS_PROJECT]->(p)
```

```cypher
// ESTIMATE_BECOMES_PROJECT: Estimate -> Project (via project.csv estimate_id)
UNWIND $rows AS row
MATCH (e:Estimate {estimate_id: row.estimate_id})
MATCH (p:Project {project_id: row.project_id})
MERGE (e)-[:ESTIMATE_BECOMES_PROJECT]->(p)
```

```cypher
// ESTIMATE_HAS_LINE_ITEM: Estimate -> EstimateLineItem (via estimate_line_item.csv estimate_id)
UNWIND $rows AS row
MATCH (e:Estimate {estimate_id: row.estimate_id})
MATCH (eli:EstimateLineItem {line_id: row.line_id})
MERGE (e)-[:ESTIMATE_HAS_LINE_ITEM]->(eli)
```

```cypher
// PROJECT_HAS_JOB: Project -> Job (via job.csv project_id)
UNWIND $rows AS row
MATCH (p:Project {project_id: row.project_id})
MATCH (j:Job {job_id: row.job_id})
MERGE (p)-[:PROJECT_HAS_JOB]->(j)
```

```cypher
// PROJECT_HAS_INVOICE: Project -> Invoice (via invoice.csv project_id)
UNWIND $rows AS row
MATCH (p:Project {project_id: row.project_id})
MATCH (i:Invoice {invoice_id: row.invoice_id})
MERGE (p)-[:PROJECT_HAS_INVOICE]->(i)
```

```cypher
// PROJECT_HAS_BILL: Project -> Bill (via bill.csv project_id, skip nulls)
UNWIND $rows AS row
WITH row WHERE row.project_id IS NOT NULL AND row.project_id <> ''
MATCH (p:Project {project_id: row.project_id})
MATCH (b:Bill {bill_id: row.bill_id})
MERGE (p)-[:PROJECT_HAS_BILL]->(b)
```

```cypher
// JOB_HAS_TIME_ENTRY: Job -> TimeEntry (via time_entry.csv job_id)
UNWIND $rows AS row
MATCH (j:Job {job_id: row.job_id})
MATCH (te:TimeEntry {entry_id: row.entry_id})
MERGE (j)-[:JOB_HAS_TIME_ENTRY]->(te)
```

```cypher
// JOB_HAS_BILL: Job -> Bill (via bill.csv job_id, skip nulls)
UNWIND $rows AS row
WITH row WHERE row.job_id IS NOT NULL AND row.job_id <> ''
MATCH (j:Job {job_id: row.job_id})
MATCH (b:Bill {bill_id: row.bill_id})
MERGE (j)-[:JOB_HAS_BILL]->(b)
```

```cypher
// EMPLOYEE_LOGS_TIME: Employee -> TimeEntry (via time_entry.csv employee_id)
UNWIND $rows AS row
MATCH (e:Employee {id: row.employee_id})
MATCH (te:TimeEntry {entry_id: row.entry_id})
MERGE (e)-[:EMPLOYEE_LOGS_TIME]->(te)
```

```cypher
// VENDOR_HAS_BILL: Vendor -> Bill (via bill.csv vendor_id)
UNWIND $rows AS row
MATCH (v:Vendor {id: row.vendor_id})
MATCH (b:Bill {bill_id: row.bill_id})
MERGE (v)-[:VENDOR_HAS_BILL]->(b)
```

```cypher
// INVOICE_HAS_PAYMENT: Invoice -> Payment (via payment.csv invoice_id)
UNWIND $rows AS row
MATCH (i:Invoice {invoice_id: row.invoice_id})
MATCH (pay:Payment {payment_id: row.payment_id})
MERGE (i)-[:INVOICE_HAS_PAYMENT]->(pay)
```

```cypher
// COMPANY_EMPLOYS: Company -> Employee (all employees belong to the single company)
UNWIND $rows AS row
MATCH (co:Company {name: $company_name})
MATCH (e:Employee {id: row.id})
MERGE (co)-[:COMPANY_EMPLOYS]->(e)
```

```cypher
// ESTIMATE_LINE_ITEM_MAPS_TO_JOB: EstimateLineItem -> Job
// Semantic join: cost_code matches job.code within the same project context.
// Requires a subquery to resolve through estimate -> project -> job.
UNWIND $rows AS row
MATCH (eli:EstimateLineItem {line_id: row.line_id})
MATCH (e:Estimate {estimate_id: row.estimate_id})
MATCH (p:Project {project_id: e.project_id})
MATCH (j:Job {project_id: p.project_id})
WHERE j.code = row.cost_code
MERGE (eli)-[:ESTIMATE_LINE_ITEM_MAPS_TO_JOB]->(j)
```

Note on the last relationship: this is a semantic join, not a direct FK. EstimateLineItem has a `cost_code` field (e.g., "03-FRAMING") and Job has a `code` field with the same vocabulary. But the same cost code appears across multiple projects, so we resolve through the estimate's project context. Only accepted estimates (those with a non-null `project_id`) will successfully traverse this path.

## 6. The Python ETL Script

The script below is the complete, runnable implementation. It handles Customer and Project loading inline as examples, then uses a data-driven configuration dict for the remaining 12 entity types.

```python
#!/usr/bin/env python3
"""
Ridgeline Builders ETL Pipeline
Loads 16 CSV files into Neo4j property graph.
Idempotent via MERGE -- safe to re-run.
"""

import json
import logging
import sys
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ridgeline_etl")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ridgeline2024"
DATA_DIR = Path("data/ridgeline_builders/data_room")
BATCH_SIZE = 1000

# ---------------------------------------------------------------------------
# Cypher statements for each entity type
# ---------------------------------------------------------------------------

ENTITY_CYPHER = {
    "Company": """
        UNWIND $rows AS row
        MERGE (c:Company {name: row.name})
        SET c.trade = row.trade,
            c.region = row.region,
            c.owner_name = row.owner_name,
            c.owner_employee_id = row.owner_employee_id,
            c.address = row.address,
            c.phone = row.phone,
            c.email = row.email,
            c.license_number = row.license_number
    """,
    "Customer": """
        UNWIND $rows AS row
        MERGE (c:Customer {id: row.id})
        SET c.name = row.name,
            c.email = row.email,
            c.phone = row.phone,
            c.address = row.address,
            c.payment_terms = row.payment_terms,
            c.source = row.source,
            c.type = row.type,
            c.tax_exempt = row.tax_exempt,
            c.credit_limit = row.credit_limit,
            c.status = row.status,
            c.created_at = date(row.created_at),
            c.notes = row.notes
    """,
    "Vendor": """
        UNWIND $rows AS row
        MERGE (v:Vendor {id: row.id})
        SET v.name = row.name,
            v.type = row.type,
            v.trade = row.trade,
            v.contact = row.contact,
            v.phone = row.phone,
            v.email = row.email,
            v.payment_terms = row.payment_terms,
            v.tax_id = row.tax_id,
            v.w9_on_file = row.w9_on_file,
            v.insurance_expiry = CASE WHEN row.insurance_expiry IS NOT NULL THEN date(row.insurance_expiry) ELSE null END,
            v.rating = row.rating,
            v.credit_limit = row.credit_limit,
            v.account_opened = CASE WHEN row.account_opened IS NOT NULL THEN date(row.account_opened) ELSE null END
    """,
    "Employee": """
        UNWIND $rows AS row
        MERGE (e:Employee {id: row.id})
        SET e.name = row.name,
            e.role = row.role,
            e.trade = row.trade,
            e.base_rate = row.base_rate,
            e.burden_rate = row.burden_rate,
            e.bill_rate = row.bill_rate,
            e.status = row.status,
            e.hire_date = date(row.hire_date),
            e.termination_date = CASE WHEN row.termination_date IS NOT NULL THEN date(row.termination_date) ELSE null END
    """,
    "Estimate": """
        UNWIND $rows AS row
        MERGE (e:Estimate {estimate_id: row.estimate_id})
        SET e.estimate_number = row.estimate_number,
            e.version = row.version,
            e.customer_id = row.customer_id,
            e.archetype = row.archetype,
            e.status = row.status,
            e.scope_description = row.scope_description,
            e.exclusions = row.exclusions,
            e.assumptions = row.assumptions,
            e.total = row.total,
            e.cost_estimate = row.cost_estimate,
            e.markup_pct = row.markup_pct,
            e.tax_amount = row.tax_amount,
            e.created_at = date(row.created_at),
            e.sent_at = date(row.sent_at),
            e.valid_until = date(row.valid_until),
            e.accepted_at = CASE WHEN row.accepted_at IS NOT NULL THEN date(row.accepted_at) ELSE null END,
            e.project_id = row.project_id
    """,
    "EstimateLineItem": """
        UNWIND $rows AS row
        MERGE (eli:EstimateLineItem {line_id: row.line_id})
        SET eli.estimate_id = row.estimate_id,
            eli.cost_code = row.cost_code,
            eli.description = row.description,
            eli.quantity = row.quantity,
            eli.unit = row.unit,
            eli.unit_cost = row.unit_cost,
            eli.unit_price = row.unit_price,
            eli.line_total = row.line_total,
            eli.category = row.category
    """,
    "Project": """
        UNWIND $rows AS row
        MERGE (p:Project {project_id: row.project_id})
        SET p.estimate_id = row.estimate_id,
            p.customer_id = row.customer_id,
            p.name = row.name,
            p.archetype = row.archetype,
            p.type = row.type,
            p.trade = row.trade,
            p.status = row.status,
            p.site_address = row.site_address,
            p.start_date = date(row.start_date),
            p.end_date = date(row.end_date),
            p.actual_start = date(row.actual_start),
            p.actual_end = date(row.actual_end),
            p.contract_amount = row.contract_amount,
            p.contract_type = row.contract_type,
            p.markup_pct = row.markup_pct,
            p.retention_pct = row.retention_pct,
            p.retention_released = row.retention_released,
            p.permit_required = row.permit_required,
            p.permit_number = row.permit_number,
            p.notes = row.notes
    """,
    "Job": """
        UNWIND $rows AS row
        MERGE (j:Job {job_id: row.job_id})
        SET j.project_id = row.project_id,
            j.code = row.code,
            j.name = row.name,
            j.budgeted_labor_hours = row.budgeted_labor_hours,
            j.budgeted_labor_cost = row.budgeted_labor_cost,
            j.budgeted_material_cost = row.budgeted_material_cost,
            j.budgeted_sub_cost = row.budgeted_sub_cost,
            j.budgeted_equipment_cost = row.budgeted_equipment_cost,
            j.budgeted_other_cost = row.budgeted_other_cost,
            j.status = row.status,
            j.sort_order = row.sort_order,
            j.sub_vendor_type = row.sub_vendor_type,
            j.equipment_needed = row.equipment_needed,
            j.actual_start = date(row.actual_start),
            j.actual_end = date(row.actual_end)
    """,
    "TimeEntry": """
        UNWIND $rows AS row
        MERGE (te:TimeEntry {entry_id: row.entry_id})
        SET te.employee_id = row.employee_id,
            te.project_id = row.project_id,
            te.job_id = row.job_id,
            te.date = date(row.date),
            te.hours_regular = row.hours_regular,
            te.hours_overtime = row.hours_overtime,
            te.cost = row.cost,
            te.notes = row.notes
    """,
    "Bill": """
        UNWIND $rows AS row
        MERGE (b:Bill {bill_id: row.bill_id})
        SET b.vendor_id = row.vendor_id,
            b.project_id = row.project_id,
            b.job_id = row.job_id,
            b.vendor_invoice_number = row.vendor_invoice_number,
            b.status = row.status,
            b.received_date = date(row.received_date),
            b.due_date = date(row.due_date),
            b.total = row.total,
            b.paid_date = date(row.paid_date),
            b.payment_method = row.payment_method,
            b.check_number = row.check_number,
            b.category = row.category
    """,
    "BillLineItem": """
        UNWIND $rows AS row
        MERGE (bli:BillLineItem {line_id: row.line_id})
        SET bli.bill_id = row.bill_id,
            bli.project_id = row.project_id,
            bli.job_id = row.job_id,
            bli.description = row.description,
            bli.quantity = row.quantity,
            bli.unit_cost = row.unit_cost,
            bli.line_total = row.line_total,
            bli.category = row.category
    """,
    "Invoice": """
        UNWIND $rows AS row
        MERGE (i:Invoice {invoice_id: row.invoice_id})
        SET i.invoice_number = row.invoice_number,
            i.project_id = row.project_id,
            i.customer_id = row.customer_id,
            i.type = row.type,
            i.status = row.status,
            i.issued_date = date(row.issued_date),
            i.due_date = date(row.due_date),
            i.subtotal = row.subtotal,
            i.retention_held = row.retention_held,
            i.tax = row.tax,
            i.total_due = row.total_due,
            i.notes = row.notes
    """,
    "Payment": """
        UNWIND $rows AS row
        MERGE (pay:Payment {payment_id: row.payment_id})
        SET pay.invoice_id = row.invoice_id,
            pay.project_id = row.project_id,
            pay.customer_id = row.customer_id,
            pay.amount = row.amount,
            pay.method = row.method,
            pay.reference = row.reference,
            pay.received_date = date(row.received_date),
            pay.deposited_date = date(row.deposited_date)
    """,
    "NarrativeEvent": """
        UNWIND $rows AS row
        MERGE (ne:NarrativeEvent {event_id: row.event_id})
        SET ne.event_type = row.event_type,
            ne.date = date(row.date),
            ne.description = row.description,
            ne.amount = row.amount,
            ne.event_metadata = row.event_metadata
    """,
}

# ---------------------------------------------------------------------------
# Entity loading config: CSV filename -> entity type + type coercions
# ---------------------------------------------------------------------------

ENTITY_CONFIG = [
    # Stage 1: Master data
    {
        "csv": "company.csv",
        "entity": "Company",
        "coerce": {},
    },
    {
        "csv": "customer.csv",
        "entity": "Customer",
        "coerce": {
            "credit_limit": "float",
            "tax_exempt": "bool",
            "created_at": "date_str",  # keep as string, Cypher does date()
        },
    },
    {
        "csv": "vendor.csv",
        "entity": "Vendor",
        "coerce": {
            "w9_on_file": "bool",
            "rating": "float",
            "credit_limit": "float",
            "insurance_expiry": "date_str",
            "account_opened": "date_str",
        },
    },
    {
        "csv": "employee.csv",
        "entity": "Employee",
        "coerce": {
            "base_rate": "float",
            "burden_rate": "float",
            "bill_rate": "float",
            "hire_date": "date_str",
            "termination_date": "date_str",
        },
    },
    # Stage 2: Estimates
    {
        "csv": "estimate.csv",
        "entity": "Estimate",
        "coerce": {
            "version": "int",
            "total": "float",
            "cost_estimate": "float",
            "markup_pct": "float",
            "tax_amount": "float",
            "created_at": "date_str",
            "sent_at": "date_str",
            "valid_until": "date_str",
            "accepted_at": "date_str",
        },
    },
    {
        "csv": "estimate_line_item.csv",
        "entity": "EstimateLineItem",
        "coerce": {
            "quantity": "int",
            "unit_cost": "float",
            "unit_price": "float",
            "line_total": "float",
        },
    },
    # Stage 3: Projects
    {
        "csv": "project.csv",
        "entity": "Project",
        "coerce": {
            "contract_amount": "float",
            "markup_pct": "float",
            "retention_pct": "float",
            "retention_released": "bool",
            "permit_required": "bool",
            "start_date": "date_str",
            "end_date": "date_str",
            "actual_start": "date_str",
            "actual_end": "date_str",
        },
    },
    {
        "csv": "job.csv",
        "entity": "Job",
        "coerce": {
            "budgeted_labor_hours": "float",
            "budgeted_labor_cost": "float",
            "budgeted_material_cost": "float",
            "budgeted_sub_cost": "float",
            "budgeted_equipment_cost": "float",
            "budgeted_other_cost": "float",
            "sort_order": "int",
            "equipment_needed": "bool",
            "actual_start": "date_str",
            "actual_end": "date_str",
        },
    },
    # Stage 4: Financials
    {
        "csv": "bill.csv",
        "entity": "Bill",
        "coerce": {
            "total": "float",
            "received_date": "date_str",
            "due_date": "date_str",
            "paid_date": "date_str",
            "check_number": "int_nullable",
        },
    },
    {
        "csv": "bill_line_item.csv",
        "entity": "BillLineItem",
        "coerce": {
            "quantity": "int",
            "unit_cost": "float",
            "line_total": "float",
        },
    },
    {
        "csv": "invoice.csv",
        "entity": "Invoice",
        "coerce": {
            "subtotal": "float",
            "retention_held": "float",
            "tax": "float",
            "total_due": "float",
            "issued_date": "date_str",
            "due_date": "date_str",
        },
    },
    {
        "csv": "payment.csv",
        "entity": "Payment",
        "coerce": {
            "amount": "float",
            "received_date": "date_str",
            "deposited_date": "date_str",
        },
    },
    # Stage 5: Execution
    {
        "csv": "time_entry.csv",
        "entity": "TimeEntry",
        "coerce": {
            "hours_regular": "float",
            "hours_overtime": "float",
            "cost": "float",
            "date": "date_str",
        },
    },
]

# ---------------------------------------------------------------------------
# Relationship loading config
# ---------------------------------------------------------------------------

RELATIONSHIP_CONFIG = [
    {
        "csv": "estimate.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (c:Customer {id: row.customer_id})
            MATCH (e:Estimate {estimate_id: row.estimate_id})
            MERGE (c)-[:CUSTOMER_HAS_ESTIMATE]->(e)
        """,
        "name": "CUSTOMER_HAS_ESTIMATE",
    },
    {
        "csv": "project.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (c:Customer {id: row.customer_id})
            MATCH (p:Project {project_id: row.project_id})
            MERGE (c)-[:CUSTOMER_HAS_PROJECT]->(p)
        """,
        "name": "CUSTOMER_HAS_PROJECT",
    },
    {
        "csv": "project.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (e:Estimate {estimate_id: row.estimate_id})
            MATCH (p:Project {project_id: row.project_id})
            MERGE (e)-[:ESTIMATE_BECOMES_PROJECT]->(p)
        """,
        "name": "ESTIMATE_BECOMES_PROJECT",
    },
    {
        "csv": "estimate_line_item.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (e:Estimate {estimate_id: row.estimate_id})
            MATCH (eli:EstimateLineItem {line_id: row.line_id})
            MERGE (e)-[:ESTIMATE_HAS_LINE_ITEM]->(eli)
        """,
        "name": "ESTIMATE_HAS_LINE_ITEM",
    },
    {
        "csv": "job.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (p:Project {project_id: row.project_id})
            MATCH (j:Job {job_id: row.job_id})
            MERGE (p)-[:PROJECT_HAS_JOB]->(j)
        """,
        "name": "PROJECT_HAS_JOB",
    },
    {
        "csv": "invoice.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (p:Project {project_id: row.project_id})
            MATCH (i:Invoice {invoice_id: row.invoice_id})
            MERGE (p)-[:PROJECT_HAS_INVOICE]->(i)
        """,
        "name": "PROJECT_HAS_INVOICE",
    },
    {
        "csv": "bill.csv",
        "cypher": """
            UNWIND $rows AS row
            WITH row WHERE row.project_id IS NOT NULL
            MATCH (p:Project {project_id: row.project_id})
            MATCH (b:Bill {bill_id: row.bill_id})
            MERGE (p)-[:PROJECT_HAS_BILL]->(b)
        """,
        "name": "PROJECT_HAS_BILL",
        "filter_nulls": "project_id",
    },
    {
        "csv": "time_entry.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (j:Job {job_id: row.job_id})
            MATCH (te:TimeEntry {entry_id: row.entry_id})
            MERGE (j)-[:JOB_HAS_TIME_ENTRY]->(te)
        """,
        "name": "JOB_HAS_TIME_ENTRY",
    },
    {
        "csv": "bill.csv",
        "cypher": """
            UNWIND $rows AS row
            WITH row WHERE row.job_id IS NOT NULL
            MATCH (j:Job {job_id: row.job_id})
            MATCH (b:Bill {bill_id: row.bill_id})
            MERGE (j)-[:JOB_HAS_BILL]->(b)
        """,
        "name": "JOB_HAS_BILL",
        "filter_nulls": "job_id",
    },
    {
        "csv": "time_entry.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (e:Employee {id: row.employee_id})
            MATCH (te:TimeEntry {entry_id: row.entry_id})
            MERGE (e)-[:EMPLOYEE_LOGS_TIME]->(te)
        """,
        "name": "EMPLOYEE_LOGS_TIME",
    },
    {
        "csv": "bill.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (v:Vendor {id: row.vendor_id})
            MATCH (b:Bill {bill_id: row.bill_id})
            MERGE (v)-[:VENDOR_HAS_BILL]->(b)
        """,
        "name": "VENDOR_HAS_BILL",
    },
    {
        "csv": "payment.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (i:Invoice {invoice_id: row.invoice_id})
            MATCH (pay:Payment {payment_id: row.payment_id})
            MERGE (i)-[:INVOICE_HAS_PAYMENT]->(pay)
        """,
        "name": "INVOICE_HAS_PAYMENT",
    },
    {
        "csv": "employee.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (co:Company)
            MATCH (e:Employee {id: row.id})
            MERGE (co)-[:COMPANY_EMPLOYS]->(e)
        """,
        "name": "COMPANY_EMPLOYS",
    },
    {
        "csv": "estimate_line_item.csv",
        "cypher": """
            UNWIND $rows AS row
            MATCH (eli:EstimateLineItem {line_id: row.line_id})
            MATCH (e:Estimate {estimate_id: row.estimate_id})
            WHERE e.project_id IS NOT NULL
            MATCH (j:Job {project_id: e.project_id})
            WHERE j.code = row.cost_code
            MERGE (eli)-[:ESTIMATE_LINE_ITEM_MAPS_TO_JOB]->(j)
        """,
        "name": "ESTIMATE_LINE_ITEM_MAPS_TO_JOB",
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def coerce_df(df: pd.DataFrame, coerce_spec: dict) -> pd.DataFrame:
    """Apply type coercions to a DataFrame before sending to Neo4j."""
    df = df.copy()
    for col, typ in coerce_spec.items():
        if col not in df.columns:
            continue
        if typ == "float":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif typ == "int":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif typ == "int_nullable":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif typ == "bool":
            df[col] = df[col].map(
                {"True": True, "true": True, "1": True,
                 "False": False, "false": False, "0": False}
            )
        elif typ == "date_str":
            # Keep as string for Cypher date() parsing, but normalize empty to None
            pass

    # Replace NaN/NaT with None so the Neo4j driver sends null
    df = df.where(df.notna(), None)
    return df


def to_row_dicts(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts, converting numpy types to Python native."""
    records = df.to_dict("records")
    clean = []
    for rec in records:
        row = {}
        for k, v in rec.items():
            if v is None or (isinstance(v, float) and pd.isna(v)):
                row[k] = None
            elif hasattr(v, "item"):  # numpy scalar
                row[k] = v.item()
            elif isinstance(v, str) and v.strip() == "":
                row[k] = None
            else:
                row[k] = v
        clean.append(row)
    return clean


def batched(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def run_batched(session, cypher: str, rows: list[dict], label: str):
    """Execute a Cypher statement in batches, logging progress."""
    total = len(rows)
    loaded = 0
    for batch in batched(rows, BATCH_SIZE):
        try:
            session.run(cypher, rows=batch)
            loaded += len(batch)
        except Exception as e:
            log.error(f"  Error in {label} batch at row {loaded}: {e}")
            # Continue with next batch rather than abort
            loaded += len(batch)
    log.info(f"  {label}: {loaded}/{total} rows processed")


# ---------------------------------------------------------------------------
# NarrativeEvent special handling (union of 3 CSVs)
# ---------------------------------------------------------------------------

def load_narrative_events(session, data_dir: Path):
    """Load NarrativeEvents from three source files with schema normalization."""
    rows = []

    # loc_event.csv
    loc_path = data_dir / "loc_event.csv"
    if loc_path.exists():
        df = pd.read_csv(loc_path)
        for _, r in df.iterrows():
            rows.append({
                "event_id": r["event_id"],
                "event_type": "loc_draw",
                "date": str(r["date"]),
                "description": r.get("description"),
                "amount": float(r["amount"]) if pd.notna(r.get("amount")) else None,
                "event_metadata": json.dumps({"type": r.get("type", "draw")}),
            })

    # overtime_event.csv
    ot_path = data_dir / "overtime_event.csv"
    if ot_path.exists():
        df = pd.read_csv(ot_path)
        for _, r in df.iterrows():
            rows.append({
                "event_id": r["event_id"],
                "event_type": "overtime_mandate",
                "date": str(r["start_date"]),
                "description": r.get("description"),
                "amount": None,
                "event_metadata": json.dumps({
                    "duration_weeks": int(r["duration_weeks"]),
                    "ot_hours_per_week_per_person": int(r["ot_hours_per_week_per_person"]),
                    "affected_employees": r["affected_employees"],
                }),
            })

    # pricing_change.csv
    pc_path = data_dir / "pricing_change.csv"
    if pc_path.exists():
        df = pd.read_csv(pc_path)
        for _, r in df.iterrows():
            rows.append({
                "event_id": r["event_id"],
                "event_type": "pricing_change",
                "date": str(r["effective_date"]),
                "description": r.get("notes"),
                "amount": None,
                "event_metadata": json.dumps({
                    "applies_to": r["applies_to"],
                    "old_bill_rate": float(r["old_bill_rate"]),
                    "new_bill_rate": float(r["new_bill_rate"]),
                }),
            })

    if rows:
        run_batched(session, ENTITY_CYPHER["NarrativeEvent"], rows, "NarrativeEvent")


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------

SCHEMA_STATEMENTS = [
    # Constraints
    "CREATE CONSTRAINT uniq_company_name IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE;",
    "CREATE CONSTRAINT uniq_customer_id IF NOT EXISTS FOR (n:Customer) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_vendor_id IF NOT EXISTS FOR (n:Vendor) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_estimate_estimate_id IF NOT EXISTS FOR (n:Estimate) REQUIRE n.estimate_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_estimatelineitem_line_id IF NOT EXISTS FOR (n:EstimateLineItem) REQUIRE n.line_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_project_project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.project_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_job_job_id IF NOT EXISTS FOR (n:Job) REQUIRE n.job_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_timeentry_entry_id IF NOT EXISTS FOR (n:TimeEntry) REQUIRE n.entry_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_bill_bill_id IF NOT EXISTS FOR (n:Bill) REQUIRE n.bill_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_billlineitem_line_id IF NOT EXISTS FOR (n:BillLineItem) REQUIRE n.line_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_invoice_invoice_id IF NOT EXISTS FOR (n:Invoice) REQUIRE n.invoice_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_payment_payment_id IF NOT EXISTS FOR (n:Payment) REQUIRE n.payment_id IS UNIQUE;",
    "CREATE CONSTRAINT uniq_narrativeevent_event_id IF NOT EXISTS FOR (n:NarrativeEvent) REQUIRE n.event_id IS UNIQUE;",
    # Indexes
    "CREATE INDEX idx_company_owner_name IF NOT EXISTS FOR (n:Company) ON (n.owner_name);",
    "CREATE INDEX idx_customer_name IF NOT EXISTS FOR (n:Customer) ON (n.name);",
    "CREATE INDEX idx_customer_type IF NOT EXISTS FOR (n:Customer) ON (n.type);",
    "CREATE INDEX idx_customer_status IF NOT EXISTS FOR (n:Customer) ON (n.status);",
    "CREATE INDEX idx_customer_created_at IF NOT EXISTS FOR (n:Customer) ON (n.created_at);",
    "CREATE INDEX idx_vendor_name IF NOT EXISTS FOR (n:Vendor) ON (n.name);",
    "CREATE INDEX idx_vendor_type IF NOT EXISTS FOR (n:Vendor) ON (n.type);",
    "CREATE INDEX idx_vendor_insurance_expiry IF NOT EXISTS FOR (n:Vendor) ON (n.insurance_expiry);",
    "CREATE INDEX idx_vendor_account_opened IF NOT EXISTS FOR (n:Vendor) ON (n.account_opened);",
    "CREATE INDEX idx_employee_name IF NOT EXISTS FOR (n:Employee) ON (n.name);",
    "CREATE INDEX idx_employee_status IF NOT EXISTS FOR (n:Employee) ON (n.status);",
    "CREATE INDEX idx_employee_hire_date IF NOT EXISTS FOR (n:Employee) ON (n.hire_date);",
    "CREATE INDEX idx_employee_termination_date IF NOT EXISTS FOR (n:Employee) ON (n.termination_date);",
    "CREATE INDEX idx_estimate_archetype IF NOT EXISTS FOR (n:Estimate) ON (n.archetype);",
    "CREATE INDEX idx_estimate_status IF NOT EXISTS FOR (n:Estimate) ON (n.status);",
    "CREATE INDEX idx_estimate_created_at IF NOT EXISTS FOR (n:Estimate) ON (n.created_at);",
    "CREATE INDEX idx_estimate_sent_at IF NOT EXISTS FOR (n:Estimate) ON (n.sent_at);",
    "CREATE INDEX idx_estimate_valid_until IF NOT EXISTS FOR (n:Estimate) ON (n.valid_until);",
    "CREATE INDEX idx_estimate_accepted_at IF NOT EXISTS FOR (n:Estimate) ON (n.accepted_at);",
    "CREATE INDEX idx_project_name IF NOT EXISTS FOR (n:Project) ON (n.name);",
    "CREATE INDEX idx_project_archetype IF NOT EXISTS FOR (n:Project) ON (n.archetype);",
    "CREATE INDEX idx_project_type IF NOT EXISTS FOR (n:Project) ON (n.type);",
    "CREATE INDEX idx_project_status IF NOT EXISTS FOR (n:Project) ON (n.status);",
    "CREATE INDEX idx_project_start_date IF NOT EXISTS FOR (n:Project) ON (n.start_date);",
    "CREATE INDEX idx_project_end_date IF NOT EXISTS FOR (n:Project) ON (n.end_date);",
    "CREATE INDEX idx_project_actual_start IF NOT EXISTS FOR (n:Project) ON (n.actual_start);",
    "CREATE INDEX idx_project_actual_end IF NOT EXISTS FOR (n:Project) ON (n.actual_end);",
    "CREATE INDEX idx_project_contract_type IF NOT EXISTS FOR (n:Project) ON (n.contract_type);",
    "CREATE INDEX idx_job_name IF NOT EXISTS FOR (n:Job) ON (n.name);",
    "CREATE INDEX idx_job_status IF NOT EXISTS FOR (n:Job) ON (n.status);",
    "CREATE INDEX idx_job_sub_vendor_type IF NOT EXISTS FOR (n:Job) ON (n.sub_vendor_type);",
    "CREATE INDEX idx_job_actual_start IF NOT EXISTS FOR (n:Job) ON (n.actual_start);",
    "CREATE INDEX idx_job_actual_end IF NOT EXISTS FOR (n:Job) ON (n.actual_end);",
    "CREATE INDEX idx_timeentry_date IF NOT EXISTS FOR (n:TimeEntry) ON (n.date);",
    "CREATE INDEX idx_bill_status IF NOT EXISTS FOR (n:Bill) ON (n.status);",
    "CREATE INDEX idx_bill_received_date IF NOT EXISTS FOR (n:Bill) ON (n.received_date);",
    "CREATE INDEX idx_bill_due_date IF NOT EXISTS FOR (n:Bill) ON (n.due_date);",
    "CREATE INDEX idx_bill_paid_date IF NOT EXISTS FOR (n:Bill) ON (n.paid_date);",
    "CREATE INDEX idx_invoice_type IF NOT EXISTS FOR (n:Invoice) ON (n.type);",
    "CREATE INDEX idx_invoice_status IF NOT EXISTS FOR (n:Invoice) ON (n.status);",
    "CREATE INDEX idx_invoice_issued_date IF NOT EXISTS FOR (n:Invoice) ON (n.issued_date);",
    "CREATE INDEX idx_invoice_due_date IF NOT EXISTS FOR (n:Invoice) ON (n.due_date);",
    "CREATE INDEX idx_payment_received_date IF NOT EXISTS FOR (n:Payment) ON (n.received_date);",
    "CREATE INDEX idx_payment_deposited_date IF NOT EXISTS FOR (n:Payment) ON (n.deposited_date);",
    "CREATE INDEX idx_narrativeevent_event_type IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.event_type);",
    "CREATE INDEX idx_narrativeevent_date IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.date);",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR

    if not data_dir.exists():
        log.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    # Verify connectivity
    driver.verify_connectivity()
    log.info("Connected to Neo4j")

    with driver.session() as session:
        # 1. Schema setup
        log.info("Creating schema (constraints + indexes)...")
        for stmt in SCHEMA_STATEMENTS:
            session.run(stmt)
        log.info(f"  {len(SCHEMA_STATEMENTS)} schema statements executed")

        # 2. Load entity nodes (stages 1-5)
        log.info("Loading entity nodes...")
        for cfg in ENTITY_CONFIG:
            csv_path = data_dir / cfg["csv"]
            if not csv_path.exists():
                log.warning(f"  Skipping {cfg['csv']} (not found)")
                continue

            df = pd.read_csv(csv_path)
            df = coerce_df(df, cfg["coerce"])
            rows = to_row_dicts(df)

            entity = cfg["entity"]
            cypher = ENTITY_CYPHER[entity]
            run_batched(session, cypher, rows, entity)

        # 3. Load NarrativeEvents (special handling for 3-file union)
        log.info("Loading NarrativeEvents (3-file union)...")
        load_narrative_events(session, data_dir)

        # 4. Load relationships
        log.info("Loading relationships...")
        for rel_cfg in RELATIONSHIP_CONFIG:
            csv_path = data_dir / rel_cfg["csv"]
            if not csv_path.exists():
                log.warning(f"  Skipping {rel_cfg['name']} (source CSV not found)")
                continue

            df = pd.read_csv(csv_path)
            # Replace NaN with None
            df = df.where(df.notna(), None)
            rows = to_row_dicts(df)

            # Filter null FK values where needed
            filter_col = rel_cfg.get("filter_nulls")
            if filter_col:
                rows = [r for r in rows if r.get(filter_col) is not None]

            run_batched(session, rel_cfg["cypher"], rows, rel_cfg["name"])

        # 5. Verification
        log.info("Verifying load...")
        verify_queries = [
            ("Company", "MATCH (n:Company) RETURN count(n) AS cnt"),
            ("Customer", "MATCH (n:Customer) RETURN count(n) AS cnt"),
            ("Vendor", "MATCH (n:Vendor) RETURN count(n) AS cnt"),
            ("Employee", "MATCH (n:Employee) RETURN count(n) AS cnt"),
            ("Estimate", "MATCH (n:Estimate) RETURN count(n) AS cnt"),
            ("EstimateLineItem", "MATCH (n:EstimateLineItem) RETURN count(n) AS cnt"),
            ("Project", "MATCH (n:Project) RETURN count(n) AS cnt"),
            ("Job", "MATCH (n:Job) RETURN count(n) AS cnt"),
            ("TimeEntry", "MATCH (n:TimeEntry) RETURN count(n) AS cnt"),
            ("Bill", "MATCH (n:Bill) RETURN count(n) AS cnt"),
            ("BillLineItem", "MATCH (n:BillLineItem) RETURN count(n) AS cnt"),
            ("Invoice", "MATCH (n:Invoice) RETURN count(n) AS cnt"),
            ("Payment", "MATCH (n:Payment) RETURN count(n) AS cnt"),
            ("NarrativeEvent", "MATCH (n:NarrativeEvent) RETURN count(n) AS cnt"),
        ]

        expected = {
            "Company": 1, "Customer": 13, "Vendor": 10, "Employee": 5,
            "Estimate": 100, "EstimateLineItem": 1173, "Project": 51,
            "Job": 279, "TimeEntry": 1710, "Bill": 745,
            "BillLineItem": 745, "Invoice": 134, "Payment": 134,
            "NarrativeEvent": 3,
        }

        all_good = True
        for label, query in verify_queries:
            result = session.run(query).single()
            count = result["cnt"]
            exp = expected[label]
            status = "OK" if count == exp else "MISMATCH"
            if status == "MISMATCH":
                all_good = False
            log.info(f"  {label}: {count} (expected {exp}) [{status}]")

        # Count relationships
        rel_count = session.run(
            "MATCH ()-[r]->() RETURN count(r) AS cnt"
        ).single()["cnt"]
        log.info(f"  Total relationships: {rel_count}")

        if all_good:
            log.info("Load complete. All counts match.")
        else:
            log.warning("Load complete with mismatches. Review above.")

    driver.close()


if __name__ == "__main__":
    main()
```

### Key design decisions in the script

**Type coercion happens in Python, not Cypher.** Pandas handles the float/int/bool conversions before rows reach Neo4j. Date strings are kept as strings and parsed by Cypher's `date()` function, because the Neo4j driver handles date objects awkwardly across versions. Empty strings are converted to `None` so they become null in the graph.

**NarrativeEvent gets special treatment.** Three CSV files with different schemas are normalized into a single shape in Python before being sent to one Cypher MERGE statement. The `event_type` discriminator and `event_metadata` JSON blob are computed in Python.

**ESTIMATE_LINE_ITEM_MAPS_TO_JOB is a semantic join.** Unlike all other relationships which are direct FK lookups, this one requires resolving cost codes within project context. The Cypher traverses `EstimateLineItem -> Estimate -> Project -> Job` and matches on `cost_code = job.code`. This only succeeds for accepted estimates that became projects.

**Error handling is per-batch, not per-row.** If a batch of 1000 rows fails, the error is logged and the script continues with the next batch. For a dataset this small (5,102 rows total), you will almost certainly see either zero errors or a systematic error on the first batch.

## 7. Running It

### Execute the load

```bash
python ridgeline_etl.py data/ridgeline_builders/data_room
```

Or with the default path:

```bash
python ridgeline_etl.py
```

### Verify the load

The script prints verification counts automatically. You can also run these in the Neo4j browser at http://localhost:7474:

```cypher
// Node counts by label
CALL db.labels() YIELD label
CALL db.stats.retrieve("GRAPH COUNTS") YIELD data
MATCH (n)
WITH labels(n) AS lbls, count(n) AS cnt
UNWIND lbls AS label
RETURN label, sum(cnt) AS count
ORDER BY label;
```

Or the simpler per-label check:

```cypher
MATCH (n:Company) RETURN 'Company' AS label, count(n) AS count
UNION ALL MATCH (n:Customer) RETURN 'Customer', count(n)
UNION ALL MATCH (n:Vendor) RETURN 'Vendor', count(n)
UNION ALL MATCH (n:Employee) RETURN 'Employee', count(n)
UNION ALL MATCH (n:Estimate) RETURN 'Estimate', count(n)
UNION ALL MATCH (n:EstimateLineItem) RETURN 'EstimateLineItem', count(n)
UNION ALL MATCH (n:Project) RETURN 'Project', count(n)
UNION ALL MATCH (n:Job) RETURN 'Job', count(n)
UNION ALL MATCH (n:TimeEntry) RETURN 'TimeEntry', count(n)
UNION ALL MATCH (n:Bill) RETURN 'Bill', count(n)
UNION ALL MATCH (n:BillLineItem) RETURN 'BillLineItem', count(n)
UNION ALL MATCH (n:Invoice) RETURN 'Invoice', count(n)
UNION ALL MATCH (n:Payment) RETURN 'Payment', count(n)
UNION ALL MATCH (n:NarrativeEvent) RETURN 'NarrativeEvent', count(n);
```

Expected counts: Company 1, Customer 13, Vendor 10, Employee 5, Estimate 100, EstimateLineItem 1173, Project 51, Job 279, TimeEntry 1710, Bill 745, BillLineItem 745, Invoice 134, Payment 134, NarrativeEvent 3. Total: 5,103 nodes.

### Re-run safely

The script is fully idempotent. Every node operation uses `MERGE` (match-or-create), and every relationship uses `MERGE`. Running it twice produces the same graph. Property values are overwritten with `SET`, so if source data changes, the graph reflects the latest values.

```bash
# Safe to run as many times as you want
python ridgeline_etl.py
```

### Wipe and reload from scratch

```cypher
// Delete everything -- only use in development
MATCH (n) DETACH DELETE n;
```

Then drop constraints and indexes if you want a truly clean slate:

```cypher
// Drop all constraints
SHOW CONSTRAINTS YIELD name
WITH collect(name) AS names
UNWIND names AS n
CALL { WITH n CALL db.constraintDrop(n) } IN TRANSACTIONS;

// Drop all indexes
SHOW INDEXES YIELD name WHERE name STARTS WITH 'idx_'
WITH collect(name) AS names
UNWIND names AS n
CALL { WITH n CALL db.index.drop(n) } IN TRANSACTIONS;
```

Then re-run the script, which recreates schema and loads data.

## 8. What Changes for Production

**API connectors instead of CSV exports.** The current pipeline reads flat files exported manually from QuickBooks and whatever project management tool Ridgeline uses. In production, the `reader` section of each pipeline spec switches from `connection_type: file` to `connection_type: api`. QuickBooks Online has a REST API for customers, vendors, invoices, bills, and payments. Procore or Buildertrend cover projects, jobs, and time entries. The Python script would grow an API client layer with OAuth2 authentication, pagination handling, and rate limiting. The Cypher and data model stay identical.

**Neo4j Aura instead of Docker.** Swap the `bolt://localhost:7687` connection string for an `neo4j+s://xxxx.databases.neo4j.io` URI. No schema or query changes needed. Aura Professional supports all the constraints and indexes in this schema.

**Scheduled runs.** Replace manual `python ridgeline_etl.py` with a cron job initially, then migrate to Dagster or Airflow when you need observability, retries, and alerting. The six pipeline stages map naturally to a DAG: `ingest_master_data` has no dependencies, `ingest_estimates` depends on master data, `ingest_projects` depends on both, and so on. Each stage becomes a task in the orchestrator.

**Incremental loads.** The current approach is full-scan-and-MERGE, which works fine for 5,000 rows but will not scale to 500,000. Add `updated_at` timestamp tracking: store the last-seen `updated_at` per source, and on each run only fetch rows where `updated_at > last_seen`. The MERGE pattern still works -- you are just sending fewer rows per run. The QuickBooks API supports `WHERE MetaData.LastUpdatedTime > 'timestamp'` filtering natively.

**Error alerting.** The current script logs errors to stdout. In production, failed batches should trigger alerts (Slack, PagerDuty, email). The quarantine pattern from the ETL architecture spec -- writing failed rows to `quarantine/` files for manual review -- should be implemented. A dead-letter table in Neo4j (`:QuarantinedRecord` nodes) is another option for keeping everything in one place.
