# Project Management Systems

Known schema patterns for project management and field operations software.
Emphasis on construction-adjacent tools (Procore, Buildertrend) and general
project tracking (Monday.com, Smartsheet).

Use when `schema_source: research` for project management software.

---

## Procore

**Vendor:** Procore Technologies
**Purpose:** Construction project management — RFIs, submittals, drawings,
budget, contracts, scheduling, daily logs, inspections

### Key Identifier Pattern
Integer IDs. REST API (`/rest/v1.0/` and `/vapid/`). Pagination via offset.
All resources scoped to a `company_id` and optionally `project_id`.

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Company | /rest/v1.0/companies | General contractor / company | Organization |
| Project | /rest/v1.0/projects | A construction project | Project |
| User | /rest/v1.0/users | System users | Person |
| Vendor | /rest/v1.0/vendors | Subcontractors, suppliers, design firms | Vendor |
| Contract | /rest/v1.1/contracts | Prime contracts and subcontracts | Contract |
| ContractLineItem | (nested in Contract) | Budget line items | — |
| BudgetLineItem | /rest/v1.0/budget_line_items | Budget detail lines | — |
| PrimeContractChangeOrder | /rest/v1.0/prime_contract_change_orders | Owner change orders | Contract |
| SubcontractChangeOrder | /rest/v1.0/commitment_change_orders | Sub change orders | Contract |
| DirectCost | /rest/v1.0/direct_costs | Non-subcontract costs | Transaction |
| Invoice | /rest/v1.0/invoices | Owner pay applications | Transaction |
| RFI | /rest/v1.0/rfis | Requests for information | — |
| Submittal | /rest/v1.0/submittals | Material/shop drawing submittals | — |
| Drawing | /rest/v1.0/drawings | Drawing log | — |
| DailyLog | /rest/v1.0/daily_logs | Field daily logs | — |
| Inspection | /rest/v1.0/inspections | Quality/safety inspections | — |
| WorkOrder | /rest/v1.0/work_orders | Field work orders | — |
| CostCode | /rest/v1.0/cost_codes | Cost code structure | — |
| WBSCode | /rest/v1.1/wbs_codes | Work breakdown structure codes | — |

### Key Relationships

```
Project.company_id → Company.id
Contract.project_id → Project.id
Contract.vendor_id → Vendor.id
BudgetLineItem.project_id → Project.id
BudgetLineItem.cost_code_id → CostCode.id
Invoice.project_id → Project.id
RFI.project_id → Project.id
User.vendor_id → Vendor.id  (user's company)
```

### Procore Data Model Notes
- **Two financial tracks**: Prime Contract (GC ↔ Owner) and Commitments/Subcontracts
  (GC ↔ Subs). Both have change orders and pay apps.
- **CostCode + CostType**: Every budget line has a cost code (scope of work) and cost
  type (Labor, Material, Equipment, Subcontract, Other). Critical for job costing.
- **WBS**: Newer projects may use WBS codes instead of flat cost codes.
- **Approved vs. Pending**: Many objects have `status` fields distinguishing
  approved, pending, draft, void. Budget should filter to approved.

---

## Buildertrend

**Vendor:** Buildertrend
**Purpose:** Residential construction — scheduling, budgets, customer portal,
selections (finishes/options), change orders, daily logs

### Key Identifier Pattern
Integer IDs. REST API (newer) or XML/file exports (older). Primarily a
residential builder tool — simpler than Procore, less structured financially.

### Core API Objects / Export Tables

| Object | Description | Candidate Entity Types |
|--------|-------------|----------------------|
| Job | A residential build project | Project |
| Contact | Customer, vendor, subcontractor | Customer, Vendor, Person |
| Lead | Sales lead (pre-project) | — |
| Proposal | Bid/proposal to customer | — |
| Schedule | Project schedule template + actual | — |
| ScheduleItem | Individual schedule tasks | — |
| Budget | Budget per job | — |
| BudgetItem | Line items in the budget | — |
| BillableItem | Revenue items on customer invoices | — |
| Expense | AP-side costs | Transaction |
| Invoice | Customer-facing invoices | Transaction |
| ChangeOrder | Customer change orders (scope + price changes) | Contract |
| Selection | Customer finish selections (cabinets, flooring, etc.) | — |
| DailyLog | Field daily reports | — |
| Message | Internal/customer messages | — |
| Document | File attachments | — |

### Key Relationships

```
Job.ContactId → Contact.Id  (customer/owner)
ScheduleItem.JobId → Job.Id
BudgetItem.JobId → Job.Id
ChangeOrder.JobId → Job.Id
Expense.JobId → Job.Id
Expense.VendorId → Contact.Id  (vendor contact)
Invoice.JobId → Job.Id
```

### Buildertrend Notes
- Much simpler schema than Procore — designed for residential builders, not
  commercial GCs. Less emphasis on formal contracts and submittal logs.
- `Contact` handles customers, subs, and vendors in one table — filter by type.
- **Selections** are a major feature: tracking what finish/option a customer picked,
  the price impact, and approval status. Maps to `Contract.ChangeOrder` semantically.

---

## Monday.com

**Vendor:** Monday.com
**Purpose:** General work management — projects, tasks, workflows, CRM, service

### Key Identifier Pattern
Integer IDs (GraphQL API). Flexible board-based structure — schema varies
by workspace and board configuration.

### Core API Objects (GraphQL)

| Object | Description | Candidate Entity Types |
|--------|-------------|----------------------|
| Board | A project, backlog, or process board | Project, Process |
| Group | A section within a board | — |
| Item | A row on a board (task, deal, issue, etc.) | Task, Initiative |
| Subitem | Child items | — |
| Column | A field definition on a board | — |
| ColumnValue | A value for a specific item+column | — |
| User | System user | Person |
| Team | Team of users | Team |
| Update | Comments/activity on an item | — |
| Doc | Monday Docs | — |
| Workspace | Top-level org unit | — |

### Key Relationships

```
Item.board_id → Board.id
Item.group_id → Group.id
Subitem.parent_item_id → Item.id
ColumnValue.item_id → Item.id
ColumnValue.column_id → Column.id
Item.creator_id → User.id
```

### Monday.com Notes
- **Flexible schema is a challenge**: Columns are user-defined. The actual
  data model is discovered per workspace — you must read board schemas before
  you know what fields exist.
- **Connect Boards** columns create cross-board relationships (equivalent to FKs).
- **People columns** link to Users — common source of staffing/assignment data.
- Common boards to look for: Project tracker, Resource planning, Bug tracker,
  Sales CRM, Employee onboarding.

---

## Smartsheet

**Vendor:** Smartsheet
**Purpose:** Spreadsheet-like project management — Gantt, resource management,
forms, automations, dashboards

### Key Identifier Pattern
Integer IDs. REST API (`/2.0/`). Row-based with columns defined per sheet.

### Core API Objects

| Object | Description | Candidate Entity Types |
|--------|-------------|----------------------|
| Sheet | A spreadsheet/project plan | Project, Process |
| Row | A row in a sheet (task, item, etc.) | Task |
| Column | A column definition | — |
| Cell | A cell value | — |
| Folder | Organizes sheets | — |
| Workspace | Top-level org unit | — |
| User | System user | Person |
| Group | Group of users | Team |
| Attachment | Files attached to rows | — |
| Discussion | Comments on rows | — |

### Key Relationships

```
Row.sheetId → Sheet.id
Row.parentId → Row.id  (hierarchy — sub-tasks)
Cell.rowId → Row.id
Cell.columnId → Column.id
```

### Smartsheet Notes
- Like Monday.com, schema is user-defined. Must inspect actual sheets to
  understand data structure.
- **Cross-sheet references**: Sheets can reference cells in other sheets —
  equivalent to computed lookups, not FK relationships.
- **Resource Management** (10,000ft by Smartsheet): separate module with
  People, Projects, Assignments, Time Entries as structured objects.

---

## Common Cross-System Patterns

### Project as the Hub
In construction and professional services, `Project` is almost always the
central hub entity. Budget, contracts, people, schedules, documents all
have `project_id` FKs. Hub-and-spoke pattern — high betweenness centrality.

### Budget vs. Actuals
All project management tools distinguish:
- **Original Budget**: What was planned
- **Approved Change Orders**: Scope changes approved by owner
- **Revised Budget**: Original + approved COs
- **Committed Costs**: Signed subcontracts + POs
- **Actual Costs**: Invoices paid
- **Projected Final Cost**: Best estimate at completion

Model these as properties on a `Budget` or `CostItem` entity, not separate entity types.

### Cost Code Hierarchies
Construction tools use cost codes (CSI MasterFormat, or custom) to categorize
work. These are usually a shallow hierarchy (division → section → code).
Map to `CostCode` as an entity type — referenced by budget lines, invoices,
and change orders alike.

### Owner / GC / Sub Triangle
In commercial construction:
- **Owner** (Client): Holds the prime contract with the GC
- **GC** (Your company typically): Manages the project, holds subcontracts
- **Subcontractors**: Execute specific scopes (MEP, concrete, steel, etc.)

This triangle creates two distinct contract chains to model:
1. PrimeContract (Owner → GC)
2. Subcontracts (GC → Subs)
Both have their own change orders, pay applications, and retention.
