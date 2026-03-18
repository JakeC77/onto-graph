# HRIS / Payroll Systems

Known schema patterns for HR information systems and payroll processors.
Use when `schema_source: research` for HR or payroll software.

---

## ADP Workforce Now

**Vendor:** ADP
**Purpose:** Payroll, HR, benefits, time & attendance, talent (mid-to-large)

### Key Identifier Pattern
ADP uses `associateOID` (a stable UUID-like string) as the canonical person
identifier across all ADP products. Also `workerID` (visible to employees).
API: ADP Marketplace REST API (`/hr/v2/workers`). Pay data via `/payroll/v1/`.

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Worker | /hr/v2/workers | Employee master (includes employment info) | Person |
| WorkAssignment | (nested in Worker) | Active job assignment | — |
| Person | (nested in Worker) | Demographic info | — |
| CustomFieldGroup | (nested in Worker) | Custom HR fields | — |
| PayStatement | /payroll/v1/pay-statements | Individual paycheck detail | Transaction |
| PayDataInput | /payroll/v1/pay-data-input | Earnings/deductions for a pay run | — |
| PayrollOutput | /payroll/v1/payroll-output | Processed payroll output | Transaction |
| TimeCard | /time/v2/workers/{id}/time-cards | Time entry | — |
| BenefitElection | /benefits/v1/benefit-elections | Benefits enrolled | — |
| OrganizationalUnit | /hr/v2/organizational-units | Departments/cost centers | Department, CostCenter |

### Key Relationships

```
Worker.workAssignments[].homeOrganizationalUnit → OrganizationalUnit
Worker.workAssignments[].reportsTo → Worker (manager FK)
Worker.workAssignments[].positionID → Position
PayStatement.associateOID → Worker.associateOID
TimeCard.associateOID → Worker.associateOID
BenefitElection.associateOID → Worker.associateOID
```

### ADP Data Model Notes
- `Worker` is a deeply nested object. `workAssignments` is an array —
  most workers have one active assignment, but multiple historical ones.
- **TermDate** in workAssignment signals termination. Filter to active workers
  with `workAssignmentStatus.statusCode.codeValue = "Active"`.
- **Reports-to** is on the WorkAssignment, not the Person — this is the correct
  place to extract org hierarchy.
- ADP exports (payroll registers, HR data files) are often flat CSV/Excel —
  column names vary by client configuration.

---

## Gusto

**Vendor:** Gusto
**Purpose:** Payroll, benefits, HR (small-to-mid market)

### Key Identifier Pattern
UUID strings for all primary keys. REST API (`/v1/`). Developer-friendly,
simpler data model than ADP.

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Company | /v1/companies/{uuid} | The employer company | Organization |
| Employee | /v1/companies/{id}/employees | Employees | Person |
| Contractor | /v1/companies/{id}/contractors | 1099 contractors | Person, Vendor |
| Location | /v1/companies/{id}/locations | Work locations | Facility |
| Department | /v1/companies/{id}/departments | Departments | Department |
| PaySchedule | /v1/companies/{id}/pay_schedules | Pay period schedule | — |
| Payroll | /v1/companies/{id}/payrolls | A processed payroll run | Transaction |
| PayrollItem | (nested in Payroll) | Per-employee pay data | — |
| BenefitPlan | /v1/companies/{id}/company_benefits | Benefit plan options | — |
| EmployeeBenefit | /v1/employees/{id}/employee_benefits | Employee enrollment | — |
| TimeOff | /v1/employees/{id}/time_off_activities | PTO and leave | — |

### Key Relationships

```
Employee.company_id → Company.uuid
Employee.department → Department.uuid
Employee.manager_id → Employee.uuid
Employee.work_location_id → Location.uuid
Payroll.pay_schedule_id → PaySchedule.uuid
PayrollItem.employee_id → Employee.uuid
EmployeeBenefit.employee_id → Employee.uuid
```

### Gusto Notes
- Simpler model than ADP — one company per account (no enterprise multi-entity).
- **Contractor vs Employee** distinction matters: different tax treatment,
  different endpoints.
- Job titles and departments are freeform strings in basic tier;
  `Department` as a structured object requires higher tier.

---

## Workday

**Vendor:** Workday
**Purpose:** Full HCM + Finance (enterprise) — HR, payroll, talent, planning,
financials, procurement

### Key Identifier Pattern
Workday IDs (WID) — opaque GUIDs. Also human-readable Employee_IDs and
Supervisory Organization IDs. SOAP-based web services (legacy) or REST API
(`/ccx/api/`). Most data extracted via Workday Studio, Integration Templates,
or RaaS (Report as a Service).

### Core Objects

| Object | Description | Candidate Entity Types |
|--------|-------------|----------------------|
| Worker | Employee or contingent worker | Person |
| Position | Defined job position (separate from worker) | Role |
| SupervisoryOrganization | Org unit with a manager | Department, Team |
| CostCenter | Financial org unit | CostCenter |
| Company | Legal entity | LegalEntity |
| BusinessUnit | Business division | Department |
| Location | Physical location | Facility |
| JobFamily | Group of related job profiles | — |
| JobProfile | A specific job definition | Role |
| CompensationGrade | Compensation band | — |
| PayGroup | Payroll group | — |
| PayResult | Payroll output per worker per period | Transaction |
| BenefitPlan | Benefit offering | — |
| PerformanceReview | Review record | — |
| LeaveRequest | Leave of absence | — |

### Key Relationships

```
Worker.PrimaryPosition → Position.WID
Position.SupervisoryOrganization → SupervisoryOrganization.WID
Worker.Manager → Worker.WID  (via SupervisoryOrganization.Manager)
SupervisoryOrganization.CostCenter → CostCenter.WID
Worker.Company → Company.WID
Worker.Location → Location.WID
PayResult.Worker → Worker.WID
```

### Workday Notes
- **SupervisoryOrganization** is the key org structure unit. It has a Manager
  and rolls up through the hierarchy. Distinct from CostCenter (financial).
- **Worker vs Position**: Workday separates the person (Worker) from the seat
  (Position). Positions can be vacant. One Worker can hold multiple Positions
  (multiple assignments).
- **Workday extracts** are typically flat reports — RaaS exports with configured
  columns. Column names are configured per client. Field mapping requires
  knowing the report design.
- Financial data (if Workday Financials): same pattern as NetSuite with
  Company (subsidiary), CostCenter, spend categories.

---

## BambooHR

**Vendor:** BambooHR
**Purpose:** Core HR — employee records, org chart, time off, performance (SMB)

### Key Identifier Pattern
Integer IDs. REST API (`/api/gateway.php/{company}/v1/`).

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Employee | /employees/{id} | Employee record | Person |
| EmployeeField | (configurable) | Any HR field | — |
| Department | (field on Employee) | Department name (freeform or list) | Department |
| Location | (field on Employee) | Work location | Facility |
| Division | (field on Employee) | Business division | Department |
| JobTitle | (field on Employee) | Job title (freeform) | Role |
| Manager | (field on Employee) | Reporting manager | Person |
| TimeOffRequest | /time_off/requests | PTO and leave requests | — |
| TimeOffPolicy | /time_off/policies | Leave policy definitions | — |
| Benefit | /benefit_plans | Benefits plans | — |
| PerformanceReview | /performance | Review records | — |
| CustomField | /meta/fields | Custom field definitions | — |

### Key Relationships

```
Employee.department → (freeform department string or list value)
Employee.supervisor → Employee.id
Employee.location → (location string)
TimeOffRequest.employeeId → Employee.id
```

### BambooHR Notes
- Simplest of the four. Many fields are freeform strings — Department, Location,
  Division may not have separate entity tables. They're attributes on Employee.
- **Custom fields** are common — clients configure their own HR fields. Must
  inspect `/meta/fields` to discover the full schema.
- Good for small/mid-market companies needing core headcount data. Less suitable
  for complex org structures.

---

## Common Cross-System Patterns

### The Person Identity Problem
Every HRIS has a person identifier. But this rarely matches the identifier in
other systems (accounting, project management, CRM). Cross-system person
matching requires:
1. Email address (most reliable cross-system key)
2. Full name (normalize: lowercase, trim, strip suffixes)
3. Employee number (if shared across systems)

Document the person identity strategy in the mapping plan.

### Org Hierarchy Models
| System | Org Unit | Manager Link |
|--------|----------|-------------|
| ADP | OrganizationalUnit | Worker.WorkAssignment.reportsTo |
| Gusto | Department | Employee.manager_id |
| Workday | SupervisoryOrganization | Worker.Manager (via org) |
| BambooHR | (freeform) | Employee.supervisor |

All can produce a `reports_to` relationship between Person entities,
but the path differs.

### Active vs. Terminated Employees
Always filter to active employees for current-state analysis. Terminated
employees are valuable for:
- Attrition analysis (who left, when, from what role)
- Historical org charts (what the structure was at a point in time)
- Key person identification (critical people who left)

Model with a `status` property and `termination_date` on Person.

### Payroll Data Sensitivity
Payroll data (compensation, tax details, bank info) is highly sensitive.
For ontology purposes, you typically only need:
- Employee exists and is active
- Department / reporting structure
- Job title / level
- Location

Gross pay amounts may be needed for financial modeling (e.g., total labor cost
by department) but should be handled with care and documented explicitly.
