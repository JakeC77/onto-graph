# Operations and Systems

## Entity Types

### Initiative

**Signals in data:**
- Columns: initiative_id, project_id, program_id, initiative_name
- Properties: status, owner, start_date, target_date, budget, progress
- Often appears in: project tracking tools, board decks, status reports

**Common confusion:**
- Initiative vs. Task: Tasks are work items within an initiative. If tasks
  have their own assignee, status, and deadline → separate entity type.
- Initiative vs. Program: Programs are groups of related initiatives. If
  the data tracks programs with their own properties → separate type.
- Initiative vs. Goal/OKR: Goals are outcomes; initiatives are efforts
  to achieve them. Different lifecycle and properties → separate types.

**Typical relationships:**
- owned_by (Initiative → Person)
- part_of (Initiative → Program)
- funded_by (Initiative → Budget/CostCenter)
- depends_on (Initiative → Initiative)
- uses (Initiative → System)

### System

**Signals in data:**
- Columns: system_id, application_id, system_name, app_name
- Properties: vendor, version, criticality, owner, cost
- Often appears in: IT asset inventories, architecture docs, cost allocation

**Common confusion:**
- System vs. Tool: If it's a shared infrastructure component with an owner
  and lifecycle → System. If it's a personal productivity tool → property.
- System vs. Service: Services are what systems provide. If services are
  tracked with their own SLAs and consumers → separate type.

**Typical relationships:**
- owned_by (System → Person/Department)
- used_by (Person/Department → System)
- depends_on (System → System)
- supports (System → Process/Initiative)

### Process

**Signals in data:**
- Columns: process_id, process_name, workflow
- Properties: owner, frequency, inputs, outputs, SLA
- May appear in: process documentation, compliance data, operational metrics

**Entity vs. property test:** If processes have their own owner, metrics, and
lifecycle → entity type. If "process" is just a category label → property.

**Typical relationships:**
- owned_by (Process → Person/Department)
- uses (Process → System)
- produces (Process → output/artifact)
- governed_by (Process → Policy/Control)

### Asset

**Signals in data:**
- Columns: asset_id, asset_tag, asset_name, serial_number
- Properties: type, location, value, depreciation, owner
- May appear in: fixed asset registers, IT inventories, facilities data

**Entity vs. property test:** If assets are tracked individually with IDs,
locations, and depreciation → entity type. If they're just line items in
a financial report → likely a property of Account.

## Operational Hierarchy Patterns

1. **Initiative hierarchy**: Task → Initiative → Program → Portfolio
2. **System hierarchy**: Component → System → Platform → Domain
3. **Process hierarchy**: Step → Process → Value Stream → Capability
4. **Location hierarchy**: Floor → Building → Campus → Region

## Red Flags

- **Shadow IT**: Systems mentioned in documents but not in IT inventory
- **Orphan initiatives**: Projects with no owner or budget linkage
- **Undocumented processes**: Processes that exist in practice but not in data
  (may appear as behavioral patterns in communication data)
- **Duplicate systems**: Same system with different names across departments
