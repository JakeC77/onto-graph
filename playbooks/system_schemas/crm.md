# CRM Systems

Known schema patterns for customer relationship management systems.
Use when `schema_source: research` for CRM software.

---

## Salesforce

**Vendor:** Salesforce
**Purpose:** Sales CRM, service, marketing, platform (enterprise to SMB with
different editions)

### Key Identifier Pattern
18-character Salesforce IDs (alphanumeric, case-insensitive in 15-char form).
REST API (`/services/data/vXX.0/`) or SOQL queries via query endpoint.
Exports via Data Loader produce CSV with standard column names.

### Core Standard Objects

| Object | API Name | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Account | Account | Company/organization (customer or prospect) | Customer, Organization |
| Contact | Contact | Individual person at an Account | Person |
| Lead | Lead | Unqualified prospect (pre-conversion) | — |
| Opportunity | Opportunity | A sales deal | — |
| OpportunityLineItem | OpportunityLineItem | Products on an Opportunity | — |
| Product2 | Product2 | Product catalog | Product |
| Pricebook2 | Pricebook2 | Price list | — |
| PricebookEntry | PricebookEntry | Price of a Product in a Pricebook | — |
| Contract | Contract | Customer contract (post-sale) | Contract |
| Order | Order | Sales order | Transaction |
| OrderItem | OrderItem | Line items on an Order | — |
| Case | Case | Support ticket | — |
| Task | Task | Activity (call, email, to-do) | — |
| Event | Event | Calendar event / meeting | — |
| User | User | Salesforce user (salesperson, manager) | Person |
| UserRole | UserRole | Role in sales hierarchy | Role |
| Group | Group | User group or queue | Team |
| RecordType | RecordType | Sub-type of an object (e.g., Enterprise vs. SMB Account) | — |
| CustomObject__c | (varies) | Client-specific custom objects | varies |

### Key Relationships

```
Contact.AccountId → Account.Id
Opportunity.AccountId → Account.Id
Opportunity.OwnerId → User.Id
OpportunityLineItem.OpportunityId → Opportunity.Id
OpportunityLineItem.PricebookEntryId → PricebookEntry.Id
PricebookEntry.Product2Id → Product2.Id
Contract.AccountId → Account.Id
Contract.OwnerId → User.Id
Order.AccountId → Account.Id
Order.ContractId → Contract.Id  (optional)
Case.AccountId → Account.Id
Case.ContactId → Contact.Id
User.UserRoleId → UserRole.Id
UserRole.ParentRoleId → UserRole.Id  (hierarchy)
```

### Salesforce Data Model Notes
- **Account is the hub**: Nearly everything links to Account. In B2B contexts,
  Account = customer company. In B2C, Contacts may exist without Accounts.
- **Lead → Opportunity conversion**: Leads are unmatched prospects. Upon
  qualification they're "converted" into Account + Contact + Opportunity.
  Historical leads may exist that were never converted.
- **RecordTypes** create logical sub-types. A single Account table may contain
  Customers, Prospects, Partners, Competitors — distinguished by RecordType.
  Always check RecordType distribution before assuming all rows are customers.
- **Custom objects** are common. Look for `__c` suffix in API names. Must
  inspect object schema to understand custom data.
- **Opportunity Stages** are client-configured. The stage → win/loss mapping
  must be discovered per engagement. "Closed Won" and "Closed Lost" are
  usually present but other stage names vary.

### Sales Hierarchy via UserRole
```
UserRole (CEO → VP Sales → Regional Manager → Account Executive)
  → maps to Person.reports_to relationships
  → UserRole.ParentRoleId is the org chart FK
```

---

## HubSpot

**Vendor:** HubSpot
**Purpose:** CRM, marketing, sales, service (SMB to mid-market, freemium entry)

### Key Identifier Pattern
Integer IDs. REST API (`/crm/v3/objects/`). Pagination via cursor (after parameter).

### Core Objects (CRM v3)

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Company | /crm/v3/objects/companies | Company/account | Customer, Organization |
| Contact | /crm/v3/objects/contacts | Individual person | Person |
| Deal | /crm/v3/objects/deals | Sales deal/opportunity | — |
| Ticket | /crm/v3/objects/tickets | Support ticket | — |
| Product | /crm/v3/objects/products | Product catalog | Product |
| LineItem | /crm/v3/objects/line_items | Products on a Deal | — |
| Quote | /crm/v3/objects/quotes | Sales quotes | — |
| Task | /crm/v3/objects/tasks | Activity task | — |
| Note | /crm/v3/objects/notes | Notes on records | — |
| Call | /crm/v3/objects/calls | Logged calls | — |
| Meeting | /crm/v3/objects/meetings | Meeting log | — |
| Email | /crm/v3/objects/emails | Email log | — |
| Owner | /crm/v3/owners | HubSpot users / owners | Person |
| Pipeline | /crm/v3/pipelines | Deal or ticket pipelines | — |
| CustomObject | /crm/v3/schemas | Client-defined custom objects | varies |

### Key Relationships (Associations)

HubSpot uses an **Associations** model — relationships between objects are
stored separately (not as FK columns on the object). Retrieve via:
`/crm/v3/associations/{fromObject}/{toObject}/batch/read`

```
Contact → Company  (many-to-many; primary company tracked separately)
Deal → Company
Deal → Contact
Deal → LineItem
Quote → Deal
Ticket → Contact
Ticket → Company
```

### HubSpot Data Model Notes
- **Associations instead of FK columns**: Unlike Salesforce, HubSpot doesn't put
  `company_id` on Contact. Associations are a separate data structure.
  To get a contact's company, query the association endpoint.
- **Owner** is an integer ID on each object. Maps to HubSpot users (salespeople,
  support reps). Not the same as Contact.
- **Deal Stage** is client-configured within a Pipeline. Must inspect pipeline
  stages to map to won/lost/active.
- **Properties**: All fields in HubSpot are "properties." Standard properties
  exist by default; custom properties are common. Inspect via `/crm/v3/properties/`
  to see all available fields and their types.
- **Marketing Hub** (if enabled): Adds email campaigns, forms, landing pages —
  these link back to Contacts.

---

## Pipedrive

**Vendor:** Pipedrive
**Purpose:** Sales CRM — pipeline-focused, deals-first (SMB)

### Key Identifier Pattern
Integer IDs. REST API (`/v1/`). Simple, straightforward schema.

### Core API Objects

| Object | Endpoint | Description | Candidate Entity Types |
|--------|----------|-------------|----------------------|
| Person | /v1/persons | Individual contact | Person |
| Organization | /v1/organizations | Company/account | Customer, Organization |
| Deal | /v1/deals | Sales deal | — |
| Product | /v1/products | Product catalog | Product |
| DealProduct | /v1/deals/{id}/products | Products attached to a deal | — |
| Stage | /v1/stages | Deal pipeline stages | — |
| Pipeline | /v1/pipelines | Sales pipelines | — |
| Activity | /v1/activities | Calls, emails, meetings, tasks | — |
| Note | /v1/notes | Notes on records | — |
| User | /v1/users | Pipedrive users | Person |
| CustomField | /v1/{objects}/fields | Custom field definitions | — |

### Key Relationships

```
Deal.person_id → Person.id
Deal.org_id → Organization.id
Deal.stage_id → Stage.id
Deal.pipeline_id → Pipeline.id
Deal.user_id → User.id  (owner)
Person.org_id → Organization.id
Activity.deal_id → Deal.id
Activity.person_id → Person.id
```

### Pipedrive Notes
- Simpler and more opinionated than Salesforce or HubSpot — deals-first.
  Everything is in service of moving deals through a pipeline.
- **Person vs Organization**: Separated (unlike HubSpot where Contact → Company
  is an association). Person has a direct `org_id` FK.
- **Custom fields**: Very common. All custom fields have a unique key (hash).
  Inspect `/v1/{object}/fields` to see all available fields.

---

## Common Cross-System Patterns

### The B2B Data Model
In B2B sales:
```
Organization (company being sold to)
  └── Contact (person at that company)
       └── Deal (active sales opportunity)
            └── Contract (executed deal)
```

This maps to ontology entity types: `Customer` (organization), `Person`
(contact), with relationship types: `works_at`, `owns_deal`, `signed_contract`.

### Pipeline Stage → Lifecycle State
Deal stages are client-configured but always represent a lifecycle:
- **Open stages**: Prospect, Qualified, Proposal, Negotiation (varies)
- **Terminal stages**: Closed Won, Closed Lost (usually named exactly this
  or similar)

Extract the stage list and classify each stage as `open` vs `closed_won`
vs `closed_lost`. Required for ARR / win rate calculations.

### Account Hierarchy (Enterprise CRM)
Large enterprise clients may have Account hierarchies:
- Ultimate Parent Account (holding company)
  → Parent Account (division or region)
    → Child Account (operating entity or location)

Salesforce: `Account.ParentId → Account.Id`
HubSpot: Custom property or association (no built-in hierarchy)
Pipedrive: No built-in hierarchy (use Organization as flat)

### CRM → Accounting Join
The key cross-system relationship is:
```
CRM Customer ←→ Accounting Customer
```
Joined on: company name (fuzzy), email domain, or a shared external ID.
This is almost never a clean FK match — requires entity resolution.
Document this as a `semantic_match` cross-system relationship with
`confidence: 0.7` (name-based) or higher if external IDs match.

### Owner / Salesperson
Every CRM has an "owner" on records — the salesperson or CSM responsible.
Owner links back to a User record. For ontology purposes:
- CRM User → maps to `Person` entity type
- Owner relationship → `manages` or `owns` relationship type
- Useful for: territory analysis, rep-level performance, key person risk
  (which deals/customers depend on a single person)
