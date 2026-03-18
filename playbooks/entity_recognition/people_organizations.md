# People and Organizations

## Entity Types

### Person

**Signals in data:**
- Columns: employee_id, emp_id, person_id, staff_id, name, first_name, last_name
- Grain: one row per person (high cardinality ID + name columns)
- Often has: hire_date, termination_date, title, level, department

**Common confusion:**
- Person vs. Role: A person holds a role. If "VP Finance" appears with
  properties (start_date, reporting_to), it might be a Role entity, not a Person.
  Test: Can multiple people hold the same role over time? If yes → Role is a
  separate entity type.
- Person vs. User: System data may have "users" that are service accounts, not people.
  Check for non-human identifiers.

**Typical relationships:**
- reports_to (Person → Person)
- member_of (Person → Department)
- holds_role (Person → Role)
- owns (Person → Initiative/Contract/System)
- approves (Person → various)

### Department

**Signals in data:**
- Columns: dept_id, department_id, department_name, division, business_unit
- Often appears as: FK in employee data, GL account hierarchy, cost center parent
- May have hierarchy: department → division → business unit

**Common confusion:**
- Department vs. Cost Center: Finance systems use cost centers; HR uses departments.
  They often overlap but aren't identical. If both exist in data, they're separate
  entity types.
- Department vs. Team: Teams are often informal or project-based; departments are
  structural. If both appear with different lifecycles → separate types.

**Typical relationships:**
- part_of (Department → Department, for hierarchy)
- led_by (Department → Person)
- has_budget (Department → Budget)

### Role

**Signals in data:**
- Columns: title, job_title, role, position, job_code
- High reuse: many people share the same role value
- May have: level, band, job_family

**Entity vs. property test:** If roles have their own properties (grade, salary band,
reporting line) and change independently of people → entity type. If it's just a
label on a person → property of Person.

### Team

**Signals in data:**
- Columns: team_id, team_name, squad, workgroup
- Usually smaller and more fluid than departments
- May appear in: project data, initiative ownership, Agile tooling

**Entity vs. property test:** If teams have members, leads, and lifespans → entity type.
If it's just a label on a person → property.

## Organizational Hierarchy Patterns

Data rooms often contain multiple overlapping hierarchies:

1. **Reporting hierarchy**: Person reports_to Person (org chart)
2. **Departmental hierarchy**: Department part_of Division part_of Business Unit
3. **Cost hierarchy**: Cost Center rolls up to GL account
4. **Project hierarchy**: Task part_of Project part_of Program

These are different relationship types, not the same hierarchy. Model each
as separate relationships with their own evidence.

## Red Flags

- **No employee ID column**: People may be identified only by name → deduplication risk
- **Multiple org charts**: Different sources show different reporting relationships
  (HR system vs. board deck vs. internal docs) → note as quality issue
- **Ghost employees**: IDs in one system that don't appear in another → cross-reference gap
