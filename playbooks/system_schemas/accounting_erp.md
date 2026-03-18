# Accounting / ERP Systems

Known schema patterns for common accounting and ERP systems.
Use when `schema_source: research` for accounting software.

---

## QuickBooks (Desktop: Pro/Premier/Enterprise; Online)

**Vendor:** Intuit
**Purpose:** General ledger, AP/AR, job costing, inventory, payroll (with payroll add-on)

### Key Identifier Gotcha
QuickBooks uses **ListID** (string GUID like `80000001-1234567890`) as primary keys,
not integer sequences. TxnID for transactions. Never assume integer PKs.

### Core Tables (Desktop via QBFC/IIF export; Online via REST API)

| Table | Description | Grain | Candidate Entity Types |
|-------|-------------|-------|----------------------|
| Customer | Customers and jobs (jobs are sub-customers) | One row per customer or job | Customer, Project |
| Vendor | Vendors and contractors | One row per vendor | Vendor |
| Employee | Employees (payroll) | One row per employee | Person |
| Item | Products, services, inventory items | One row per item | Product, Service |
| Account | Chart of accounts (GL accounts) | One row per account | Account |
| Class | Classes for cost tracking (optional, user-defined) | One row per class | CostCenter, Department |
| Department | Departments (QB Online; maps to Class in Desktop) | One row per dept | Department |
| Invoice | AR invoices | One row per invoice | Transaction |
| InvoiceLine | Line items on invoices | One row per line | — |
| Bill | AP bills (vendor invoices) | One row per bill | Transaction |
| BillLine | Line items on bills | One row per line | — |
| BillPaymentCheck | Payments made against bills | One row per payment | Transaction |
| ReceivePayment | Payments received from customers | One row per payment | Transaction |
| JournalEntry | Manual GL journal entries | One row per entry | Transaction |
| JournalEntryLine | Lines on journal entries | One row per line | — |
| Estimate | Quotes/estimates to customers | One row per estimate | — |
| PurchaseOrder | POs to vendors | One row per PO | — |
| TimeTracking | Time entries (if time tracking enabled) | One row per entry | — |
| PayrollItem | Payroll wage/deduction items | One row per item | — |

### Key Relationships

```
Invoice.CustomerRef → Customer.ListID
Invoice.ClassRef → Class.ListID (optional)
InvoiceLine.ItemRef → Item.ListID
Bill.VendorRef → Vendor.ListID
BillLine.ItemRef → Item.ListID
JournalEntryLine.AccountRef → Account.ListID
Customer.ParentRef → Customer.ListID  (jobs are sub-customers)
TimeTracking.EmployeeRef → Employee.ListID
TimeTracking.CustomerRef → Customer.ListID  (job costing link)
```

### Job Costing Pattern
Jobs are represented as **sub-customers** (Customer with a ParentRef). Revenue,
costs, and time are all linked to the Job (sub-customer), not the parent Customer.
When you see `CustomerRef` on transactions, it may point to a Job-level entity.

### QuickBooks Online vs Desktop
- QBO: REST API (`/v3/company/{realmId}/query`), JSON responses, cursor-based pagination
- QB Desktop: QBFC SDK, XML, or IIF flat file exports
- Table names differ slightly (QBO uses `department` instead of `class` for some purposes)

---

## Sage 100 / Sage 300

**Vendor:** Sage
**Purpose:** Accounting, distribution, manufacturing (mid-market ERP)

### Key Identifier Pattern
Sage uses module-prefixed table names: `AR_` (Accounts Receivable), `AP_`
(Accounts Payable), `GL_` (General Ledger), `PR_` (Payroll), `IM_` (Inventory
Management), `SO_` (Sales Order), `PO_` (Purchase Order).

### Core Tables

| Table | Description | Candidate Entity Types |
|-------|-------------|----------------------|
| AR_Customer | Customer master | Customer |
| AR_Invoice | AR invoices | Transaction |
| AR_InvoiceHistoryHeader | Posted invoice history | Transaction |
| AP_Vendor | Vendor master | Vendor |
| AP_Invoice | AP invoices (open) | Transaction |
| AP_InvoiceHistoryHeader | Posted AP invoice history | Transaction |
| GL_Account | Chart of accounts | Account |
| GL_DetailPostingHistory | GL transaction detail | Transaction |
| PR_Employee | Employee master | Person |
| PR_CheckHistory | Payroll check history | Transaction |
| IM_ItemMaster | Inventory items | Product |
| IM_WarehouseCode | Warehouse/location master | Facility |
| SO_SalesOrderHeader | Sales order header | Transaction |
| SO_SalesOrderDetail | Sales order lines | — |
| PO_PurchaseOrderHeader | Purchase order header | Transaction |
| CI_Item | Cross-module item (Common Items) | Product |

### Key Relationships

```
AR_Invoice.CustomerNo → AR_Customer.CustomerNo
AP_Invoice.VendorNo → AP_Vendor.VendorNo
GL_DetailPostingHistory.AccountKey → GL_Account.AccountKey
SO_SalesOrderHeader.CustomerNo → AR_Customer.CustomerNo
PR_Employee.DepartmentCode → (GL department codes)
```

---

## Xero

**Vendor:** Xero
**Purpose:** Accounting, payroll (via add-on), small-to-mid-market

### Key Identifier Pattern
Uses GUID-format IDs (UUID strings) for all primary keys. REST API only —
no database export (Xero is cloud-only).

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Contact | /Contacts | Customers and vendors combined | Customer, Vendor |
| Account | /Accounts | Chart of accounts | Account |
| Invoice | /Invoices | AR invoices (Type=ACCREC) and AP bills (Type=ACCPAY) | Transaction |
| CreditNote | /CreditNotes | Credit notes for customers/vendors | Transaction |
| BankTransaction | /BankTransactions | Bank statement lines | Transaction |
| Payment | /Payments | Payments applied to invoices | Transaction |
| Employee | /Employees | Employees (if Xero Payroll enabled) | Person |
| PayRun | /PayRuns | Payroll runs | Transaction |
| TrackingCategory | /TrackingCategories | Dimensions (like QB Classes) | CostCenter, Department |
| Item | /Items | Inventory/service items | Product, Service |

### Key Relationships

```
Invoice.Contact → Contact (by ContactID)
Invoice.LineItems[].AccountCode → Account (by Code)
Invoice.LineItems[].Tracking → TrackingCategory
Payment.Invoice → Invoice (by InvoiceID)
```

### Xero Gotcha
Contacts serve double duty — both customers and vendors are Contact objects.
Distinguish via `IsCustomer: true` / `IsSupplier: true` flags. One Contact
can be both.

---

## NetSuite (Oracle NetSuite)

**Vendor:** Oracle
**Purpose:** Full ERP — GL, AP/AR, inventory, manufacturing, CRM, HR (enterprise)

### Key Identifier Pattern
Integer internal IDs (internalid). Supports SuiteAnalytics for direct SQL access
to saved searches or SuiteQL for analytics queries.

### Core Tables (SuiteQL)

| Table | Description | Candidate Entity Types |
|-------|-------------|----------------------|
| transaction | All transactions (invoices, bills, journals, etc.) | Transaction |
| transactionline | Transaction line items | — |
| entity | All entities (customers, vendors, employees, contacts) | Customer, Vendor, Person |
| account | Chart of accounts | Account |
| item | Products and services | Product, Service |
| department | Departments | Department |
| class | Classes/cost centers | CostCenter |
| location | Locations/facilities | Facility |
| employee | Employee master (subset of entity) | Person |
| vendor | Vendor master (subset of entity) | Vendor |
| customer | Customer master (subset of entity) | Customer |
| project | Projects (if Project Management module) | Project |
| projecttask | Project tasks | — |
| subsidiary | Legal entities / subsidiaries | LegalEntity |
| currency | Currencies | — |

### Key Relationships

```
transaction.entity → entity.id
transaction.subsidiary → subsidiary.id
transactionline.account → account.id
transactionline.department → department.id
transactionline.class → class.id
transactionline.location → location.id
entity.subsidiary → subsidiary.id
```

### NetSuite Gotcha
The `transaction` table covers ALL transaction types — invoices, bills,
journal entries, payments, etc. Distinguish by `recordtype` column
(e.g., `invoice`, `vendorbill`, `journalentry`). Similarly `entity` covers
customers, vendors, and employees — use `type` column to distinguish.

### Multi-Entity Support
NetSuite natively supports multiple subsidiaries. The `subsidiary` table is
a first-class entity. Intercompany transactions are tracked via
`intercompanytype` flag on transactions.

---

## Common Cross-System Patterns

### Chart of Accounts Mapping
All accounting systems have a CoA (Account table). When mapping to ontology:
- `Account` is always an entity type
- `type` or `accounttype` column distinguishes: Asset, Liability, Equity,
  Revenue, Expense
- Hierarchical CoA (parent accounts) → model with `parent_account` relationship

### Dimensions / Cost Centers
- QuickBooks: `Class` + `Department` (QBO)
- Sage: `Division` codes on GL lines
- Xero: `TrackingCategory`
- NetSuite: `Department` + `Class` + `Location`

All map to `CostCenter` and/or `Department` entity types. Often the same
logical concept under different names.

### Job Costing
Builder/contractor clients often use job costing:
- QuickBooks: Sub-customer = Job. Costs/revenue booked to Job.
- Sage: SO_SalesOrder + IM_ = project/job tracking
- NetSuite: Project module with projecttask and timesheet tables
