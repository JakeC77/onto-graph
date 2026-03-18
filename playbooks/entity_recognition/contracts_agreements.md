# Contracts and Agreements

## Entity Types

### Contract

**Signals in data:**
- Columns: contract_id, agreement_id, contract_name, contract_number
- Properties: start_date, end_date, value, status, type
- Often has: counterparty, owner, renewal terms

**Common confusion:**
- Contract vs. Order: Contracts are agreements; orders are transactions
  under a contract. If orders have their own lifecycle → separate type.
- Contract vs. Provision: A provision is a clause within a contract. If
  provisions are tracked individually (key-person, change-of-control,
  non-compete) → Provision is a separate entity type.
- Customer contract vs. Vendor contract: Often in different systems with
  different structures. Model as separate entity types if they have
  different properties or different sources.

**Typical relationships:**
- has_party (Contract → Customer/Vendor)
- owned_by (Contract → Person)
- has_provision (Contract → Provision)
- governs (Contract → RevenueSegment/Service)

### Provision

**Signals in data:**
- Columns: provision_type, clause, term_type
- Appears within: contract detail data, legal review documents
- Types: key_person, change_of_control, non_compete, termination, renewal

**Entity vs. property test:** If provisions are tracked with their own status,
trigger conditions, and counterparty obligations → entity type. If they're
just boolean flags on a contract → properties.

### Counterparty

**Signals in data:**
- Columns: customer_id, vendor_id, client_id, supplier_id, party_name
- May be: Customer, Vendor, Partner, Guarantor
- Properties: name, industry, credit_rating, relationship_status

**Common confusion:**
- Customer vs. Counterparty: Customer is a role a counterparty plays.
  If an entity is both a customer and a vendor (common in complex businesses),
  model as a single Counterparty type with relationship roles.

## Contract Relationship Patterns

Contracts create webs of relationships:

1. **Party relationships**: Who is bound by the contract
2. **Asset relationships**: What the contract governs (services, products, IP)
3. **Financial relationships**: Payment terms, revenue recognition, cost allocation
4. **Dependency relationships**: Contracts that reference other contracts (master → sub-agreements)
5. **Temporal relationships**: Renewal chains, amendment history

## Separation-Relevant Signals

For carveout/separation engagements, watch for:
- **Assignment clauses**: Can the contract be transferred?
- **Change-of-control provisions**: What triggers on ownership change?
- **Consent requirements**: Do counterparties need to approve transfer?
- **Cross-default provisions**: Does default on one contract trigger others?

These may need to be modeled as relationship properties or as separate
Provision entities.

## Red Flags

- **No contract IDs**: Contracts identified only by name → deduplication risk
- **Missing counterparty data**: Contracts without identified parties
- **Expired contracts still in system**: Status field unreliable → verify against dates
- **Revenue without contracts**: Revenue data that doesn't link to any contract → gap
