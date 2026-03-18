# Contractual Relationships

Relationships defined by legal agreements between parties. High confidence
when sourced from contract data; lower when inferred from financial data alone.

## Party Relationships

- **has_party** (Contract → Counterparty)
  - Every contract has at least two parties
  - Roles: buyer, seller, licensor, licensee, guarantor, indemnitor
  - Properties: party_role, obligations, rights

- **guarantees** (Entity → Contract)
  - Parent companies guaranteeing subsidiary obligations
  - Personal guarantees by key people
  - Properties: guarantee_type, limit, conditions

## Provision-Based Relationships

Contract provisions create implicit relationships:

- **key_person** (Contract → Person)
  - Key person provisions tie specific people to contract validity
  - If the person leaves → contract may be terminable
  - Properties: provision_type, consequence

- **change_of_control** (Contract → Company)
  - CoC provisions trigger on ownership changes
  - Critical for M&A and carveout analysis
  - Properties: trigger_threshold, consent_required, termination_right

- **cross_default** (Contract → Contract)
  - Default on contract A triggers default on contract B
  - Creates chains of contractual risk
  - Properties: trigger_conditions, cure_period

## Service Relationships

- **provides_service** (Vendor → Company, via Contract)
  - TSAs (Transition Service Agreements) in separations
  - Outsourcing agreements
  - SaaS/licensing agreements
  - Properties: service_type, SLA, cost, duration

- **depends_on_service** (Process/System → Contract)
  - Operations that depend on contracted services
  - If the contract terminates → operational impact
  - Properties: criticality, alternatives

## Contract Network Patterns

Contracts rarely exist in isolation. Common network patterns:

1. **Master-sub structure**: Master agreement with multiple sub-agreements
   (e.g., MSA + SOWs, or umbrella agreement + country-specific addenda)

2. **Amendment chains**: Original contract → Amendment 1 → Amendment 2
   (each amendment modifies terms, the latest prevails)

3. **Renewal chains**: Contract → Renewal → Renewal
   (terms may change at each renewal)

4. **Related agreements**: Contract A references Contract B
   (non-compete tied to employment agreement, for example)

Model each pattern as explicit relationships. The contract network
is often critical for understanding organizational risk.

## Red Flags

- **Unsigned contracts in the system**: Status doesn't mean "active"
- **Expired but referenced**: Old contracts still referenced by active processes
- **Missing counterparty data**: Contracts without identified parties
- **Conflicting terms**: Multiple contracts with same counterparty that conflict
