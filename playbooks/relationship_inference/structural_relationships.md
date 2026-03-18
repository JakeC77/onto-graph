# Structural Relationships

Relationships that are explicitly encoded in the data structure — foreign keys,
hierarchy columns, junction tables. These are the highest-confidence relationships.

## Discovery from Join Candidates

Phase 0's `detect_joins.py` produces a join-key candidate matrix. Each high-confidence
join implies a relationship:

| Join Pattern | Relationship Pattern |
|-------------|---------------------|
| employees.dept_id → departments.dept_id | member_of (Person → Department) |
| contracts.owner_id → employees.emp_id | owned_by (Contract → Person) |
| org.manager_id → employees.emp_id | reports_to (Person → Person) |
| contract_parties.contract_id + customer_id | has_party (Contract ↔ Customer) via junction |

**From FK to relationship:**
1. Identify the two entity types connected by the FK
2. Determine directionality: the table with the FK "belongs to" the referenced table
3. Determine cardinality: FK column unique → 1:1; FK column not unique → N:1
4. Name the relationship based on semantic meaning (not "has_dept_id" but "member_of")

## Hierarchy Detection

Self-referential FKs indicate hierarchy:

- `employees.manager_id → employees.emp_id` → reports_to hierarchy
- `departments.parent_dept_id → departments.dept_id` → part_of hierarchy
- `accounts.parent_account → accounts.account_id` → rolls_up_to hierarchy

**Hierarchy properties:**
- Depth: How many levels? (flat org vs. deep hierarchy)
- Breadth: Average children per parent? (narrow vs. wide)
- Completeness: Does every entity have a parent? (orphans = data quality issue)

## Junction Tables

Tables whose primary purpose is to link two entity types:

**Signals:**
- Two FK columns, each pointing to a different entity type
- Row count close to the product of the two entity types (many-to-many)
- Minimal own properties (maybe just a date or status)

**Examples:**
- `team_members` (person_id, team_id, role, start_date) → member_of (Person ↔ Team)
- `contract_parties` (contract_id, party_id, party_role) → has_party (Contract ↔ Party)
- `system_users` (system_id, person_id, access_level) → uses (Person ↔ System)

The junction table's own columns become properties on the relationship.

## Column References (Non-FK)

Sometimes relationships are encoded as column values rather than formal FKs:

- `initiative.owner_name` contains a person's name (not their ID)
- `department.head_title` contains a role title (not a person ID)
- `contract.customer` contains a company name (not a customer ID)

These are lower confidence than FK joins because:
- Name matching is ambiguous (multiple "John Smith"?)
- No referential integrity enforcement
- Values may be stale or inconsistent

Flag these with confidence < 0.7 and note the ambiguity.

## Composite Keys

Some relationships require composite keys to identify:

- `financial_data` joins to `departments` on (cost_center + fiscal_year)
- `employee_performance` joins to `employees` on (emp_id + review_period)

Phase 0's join detection may miss these. Look for tables where no single
column uniquely identifies rows but combinations do.
