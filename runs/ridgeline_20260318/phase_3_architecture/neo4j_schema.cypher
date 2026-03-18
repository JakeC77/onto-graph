// Neo4j Schema generated from ontology
// Source: runs/ridgeline_20260318/phase_1_ontology/ontology.yaml
// Generated: 2026-03-18T22:33:48.431751Z
// Entity types: 14
// Relationship types: 14

// === UNIQUENESS CONSTRAINTS ===

// Company — unique on name
CREATE CONSTRAINT uniq_company_name IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE;

// Customer — unique on id
CREATE CONSTRAINT uniq_customer_id IF NOT EXISTS FOR (n:Customer) REQUIRE n.id IS UNIQUE;

// Vendor — unique on id
CREATE CONSTRAINT uniq_vendor_id IF NOT EXISTS FOR (n:Vendor) REQUIRE n.id IS UNIQUE;

// Employee — unique on id
CREATE CONSTRAINT uniq_employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE;

// Estimate — unique on estimate_id
CREATE CONSTRAINT uniq_estimate_estimate_id IF NOT EXISTS FOR (n:Estimate) REQUIRE n.estimate_id IS UNIQUE;

// EstimateLineItem — unique on line_id
CREATE CONSTRAINT uniq_estimatelineitem_line_id IF NOT EXISTS FOR (n:EstimateLineItem) REQUIRE n.line_id IS UNIQUE;

// Project — unique on project_id
CREATE CONSTRAINT uniq_project_project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.project_id IS UNIQUE;

// Job — unique on job_id
CREATE CONSTRAINT uniq_job_job_id IF NOT EXISTS FOR (n:Job) REQUIRE n.job_id IS UNIQUE;

// TimeEntry — unique on entry_id
CREATE CONSTRAINT uniq_timeentry_entry_id IF NOT EXISTS FOR (n:TimeEntry) REQUIRE n.entry_id IS UNIQUE;

// Bill — unique on bill_id
CREATE CONSTRAINT uniq_bill_bill_id IF NOT EXISTS FOR (n:Bill) REQUIRE n.bill_id IS UNIQUE;

// BillLineItem — unique on line_id
CREATE CONSTRAINT uniq_billlineitem_line_id IF NOT EXISTS FOR (n:BillLineItem) REQUIRE n.line_id IS UNIQUE;

// Invoice — unique on invoice_id
CREATE CONSTRAINT uniq_invoice_invoice_id IF NOT EXISTS FOR (n:Invoice) REQUIRE n.invoice_id IS UNIQUE;

// Payment — unique on payment_id
CREATE CONSTRAINT uniq_payment_payment_id IF NOT EXISTS FOR (n:Payment) REQUIRE n.payment_id IS UNIQUE;

// NarrativeEvent — unique on event_id
CREATE CONSTRAINT uniq_narrativeevent_event_id IF NOT EXISTS FOR (n:NarrativeEvent) REQUIRE n.event_id IS UNIQUE;

// === INDEXES ===

// Company.owner_name (BTREE)
CREATE INDEX idx_company_owner_name IF NOT EXISTS FOR (n:Company) ON (n.owner_name);

// Customer.name (BTREE)
CREATE INDEX idx_customer_name IF NOT EXISTS FOR (n:Customer) ON (n.name);

// Customer.type (BTREE)
CREATE INDEX idx_customer_type IF NOT EXISTS FOR (n:Customer) ON (n.type);

// Customer.status (BTREE)
CREATE INDEX idx_customer_status IF NOT EXISTS FOR (n:Customer) ON (n.status);

// Customer.created_at (RANGE)
CREATE INDEX idx_customer_created_at IF NOT EXISTS FOR (n:Customer) ON (n.created_at);

// Vendor.name (BTREE)
CREATE INDEX idx_vendor_name IF NOT EXISTS FOR (n:Vendor) ON (n.name);

// Vendor.type (BTREE)
CREATE INDEX idx_vendor_type IF NOT EXISTS FOR (n:Vendor) ON (n.type);

// Vendor.insurance_expiry (RANGE)
CREATE INDEX idx_vendor_insurance_expiry IF NOT EXISTS FOR (n:Vendor) ON (n.insurance_expiry);

// Vendor.account_opened (RANGE)
CREATE INDEX idx_vendor_account_opened IF NOT EXISTS FOR (n:Vendor) ON (n.account_opened);

// Employee.name (BTREE)
CREATE INDEX idx_employee_name IF NOT EXISTS FOR (n:Employee) ON (n.name);

// Employee.status (BTREE)
CREATE INDEX idx_employee_status IF NOT EXISTS FOR (n:Employee) ON (n.status);

// Employee.hire_date (RANGE)
CREATE INDEX idx_employee_hire_date IF NOT EXISTS FOR (n:Employee) ON (n.hire_date);

// Employee.termination_date (RANGE)
CREATE INDEX idx_employee_termination_date IF NOT EXISTS FOR (n:Employee) ON (n.termination_date);

// Estimate.archetype (BTREE)
CREATE INDEX idx_estimate_archetype IF NOT EXISTS FOR (n:Estimate) ON (n.archetype);

// Estimate.status (BTREE)
CREATE INDEX idx_estimate_status IF NOT EXISTS FOR (n:Estimate) ON (n.status);

// Estimate.created_at (RANGE)
CREATE INDEX idx_estimate_created_at IF NOT EXISTS FOR (n:Estimate) ON (n.created_at);

// Estimate.sent_at (RANGE)
CREATE INDEX idx_estimate_sent_at IF NOT EXISTS FOR (n:Estimate) ON (n.sent_at);

// Estimate.valid_until (RANGE)
CREATE INDEX idx_estimate_valid_until IF NOT EXISTS FOR (n:Estimate) ON (n.valid_until);

// Estimate.accepted_at (RANGE)
CREATE INDEX idx_estimate_accepted_at IF NOT EXISTS FOR (n:Estimate) ON (n.accepted_at);

// Project.name (BTREE)
CREATE INDEX idx_project_name IF NOT EXISTS FOR (n:Project) ON (n.name);

// Project.archetype (BTREE)
CREATE INDEX idx_project_archetype IF NOT EXISTS FOR (n:Project) ON (n.archetype);

// Project.type (BTREE)
CREATE INDEX idx_project_type IF NOT EXISTS FOR (n:Project) ON (n.type);

// Project.status (BTREE)
CREATE INDEX idx_project_status IF NOT EXISTS FOR (n:Project) ON (n.status);

// Project.start_date (RANGE)
CREATE INDEX idx_project_start_date IF NOT EXISTS FOR (n:Project) ON (n.start_date);

// Project.end_date (RANGE)
CREATE INDEX idx_project_end_date IF NOT EXISTS FOR (n:Project) ON (n.end_date);

// Project.actual_start (RANGE)
CREATE INDEX idx_project_actual_start IF NOT EXISTS FOR (n:Project) ON (n.actual_start);

// Project.actual_end (RANGE)
CREATE INDEX idx_project_actual_end IF NOT EXISTS FOR (n:Project) ON (n.actual_end);

// Project.contract_type (BTREE)
CREATE INDEX idx_project_contract_type IF NOT EXISTS FOR (n:Project) ON (n.contract_type);

// Job.name (BTREE)
CREATE INDEX idx_job_name IF NOT EXISTS FOR (n:Job) ON (n.name);

// Job.status (BTREE)
CREATE INDEX idx_job_status IF NOT EXISTS FOR (n:Job) ON (n.status);

// Job.sub_vendor_type (BTREE)
CREATE INDEX idx_job_sub_vendor_type IF NOT EXISTS FOR (n:Job) ON (n.sub_vendor_type);

// Job.actual_start (RANGE)
CREATE INDEX idx_job_actual_start IF NOT EXISTS FOR (n:Job) ON (n.actual_start);

// Job.actual_end (RANGE)
CREATE INDEX idx_job_actual_end IF NOT EXISTS FOR (n:Job) ON (n.actual_end);

// TimeEntry.date (RANGE)
CREATE INDEX idx_timeentry_date IF NOT EXISTS FOR (n:TimeEntry) ON (n.date);

// Bill.status (BTREE)
CREATE INDEX idx_bill_status IF NOT EXISTS FOR (n:Bill) ON (n.status);

// Bill.received_date (RANGE)
CREATE INDEX idx_bill_received_date IF NOT EXISTS FOR (n:Bill) ON (n.received_date);

// Bill.due_date (RANGE)
CREATE INDEX idx_bill_due_date IF NOT EXISTS FOR (n:Bill) ON (n.due_date);

// Bill.paid_date (RANGE)
CREATE INDEX idx_bill_paid_date IF NOT EXISTS FOR (n:Bill) ON (n.paid_date);

// Invoice.type (BTREE)
CREATE INDEX idx_invoice_type IF NOT EXISTS FOR (n:Invoice) ON (n.type);

// Invoice.status (BTREE)
CREATE INDEX idx_invoice_status IF NOT EXISTS FOR (n:Invoice) ON (n.status);

// Invoice.issued_date (RANGE)
CREATE INDEX idx_invoice_issued_date IF NOT EXISTS FOR (n:Invoice) ON (n.issued_date);

// Invoice.due_date (RANGE)
CREATE INDEX idx_invoice_due_date IF NOT EXISTS FOR (n:Invoice) ON (n.due_date);

// Payment.received_date (RANGE)
CREATE INDEX idx_payment_received_date IF NOT EXISTS FOR (n:Payment) ON (n.received_date);

// Payment.deposited_date (RANGE)
CREATE INDEX idx_payment_deposited_date IF NOT EXISTS FOR (n:Payment) ON (n.deposited_date);

// NarrativeEvent.event_type (BTREE)
CREATE INDEX idx_narrativeevent_event_type IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.event_type);

// NarrativeEvent.date (RANGE)
CREATE INDEX idx_narrativeevent_date IF NOT EXISTS FOR (n:NarrativeEvent) ON (n.date);

// === RELATIONSHIP TYPES ===
// (No DDL needed — relationships are created implicitly)

// (:Customer)-[:CUSTOMER_HAS_ESTIMATE]->(:Estimate) [1:N]
// (:Customer)-[:CUSTOMER_HAS_PROJECT]->(:Project) [1:N]
// (:Estimate)-[:ESTIMATE_BECOMES_PROJECT]->(:Project) [1:1]
// (:Estimate)-[:ESTIMATE_HAS_LINE_ITEM]->(:EstimateLineItem) [1:N]
// (:Project)-[:PROJECT_HAS_JOB]->(:Job) [1:N]
// (:Project)-[:PROJECT_HAS_INVOICE]->(:Invoice) [1:N]
// (:Project)-[:PROJECT_HAS_BILL]->(:Bill) [1:N]
// (:Job)-[:JOB_HAS_TIME_ENTRY]->(:TimeEntry) [1:N]
// (:Job)-[:JOB_HAS_BILL]->(:Bill) [1:N]
// (:Employee)-[:EMPLOYEE_LOGS_TIME]->(:TimeEntry) [1:N]
// (:Vendor)-[:VENDOR_HAS_BILL]->(:Bill) [1:N]
// (:Invoice)-[:INVOICE_HAS_PAYMENT]->(:Payment) [1:1]
// (:Company)-[:COMPANY_EMPLOYS]->(:Employee) [1:N]
// (:EstimateLineItem)-[:ESTIMATE_LINE_ITEM_MAPS_TO_JOB]->(:Job) [N:1]

// Total: 14 constraints, 46 indexes, 14 relationship types