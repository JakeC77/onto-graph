# Financial Relationships

Relationships revealed by following the money — cost allocation, revenue flows,
and budget linkages. High confidence when backed by accounting data.

## Cost Allocation Relationships

From GL/cost data:

- **funded_by** (Initiative/Department → Budget/CostCenter)
  - Evidence: cost allocation tables, GL entries tagged to cost centers
  - Properties: amount, percentage, period

- **cost_dependency** (Department → Department)
  - Evidence: internal cost allocations, shared services charges
  - A department that charges another for services creates a dependency
  - Properties: annual_cost, service_type

- **cost_bearer** (CostCenter → Entity)
  - Evidence: GL entries, budget vs. actual reports
  - Which cost center pays for which initiatives, systems, people

## Revenue Flow Relationships

From revenue/billing data:

- **generates_revenue** (Contract/Customer → RevenueSegment)
  - Evidence: billing data, revenue recognition schedules
  - Properties: amount, revenue_type (recurring, one-time), period

- **revenue_concentration** (Customer → Company)
  - Evidence: customer revenue data
  - If one customer provides > 10% of revenue → material relationship
  - Properties: revenue_share, trend

## Budget Linkage Relationships

From planning/budget data:

- **budget_allocated_to** (Budget → Department/Initiative/CostCenter)
  - Evidence: budget files, planning documents
  - Properties: amount, period, version (draft, approved, revised)

- **budget_variance** relationships connect planned to actual:
  - Budget → Actual through the same cost center or initiative
  - Variance direction and magnitude are relationship properties

## Financial Entity Chains

Financial data often reveals entity chains:

```
Customer → Contract → Revenue → Account → CostCenter → Department → Person
```

Each link in this chain is a relationship. Following the full chain
connects people to revenue sources through organizational structure.

## Intercompany Relationships

For multi-entity companies:

- **intercompany_transaction** (Entity → Entity)
  - Transfer pricing, management fees, royalties
  - These can inflate or obscure true financials
  - Important for separation analysis

## Inference from Financial Proximity

Entities that share financial dimensions may be related:
- Same cost center → probably same organizational unit
- Same revenue segment → probably same market focus
- Same budget line → probably same initiative family

These are lower confidence (shared financial category ≠ direct relationship)
but useful for discovering implicit organizational connections.
