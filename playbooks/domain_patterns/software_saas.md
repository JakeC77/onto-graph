# Software / SaaS

Common ontology patterns for SaaS businesses and technology companies.

## Typical Entity Types

| Entity Type | Signals | Notes |
|------------|---------|-------|
| Employee | HR data | Includes engineering, sales, CS, ops |
| Customer / Account | CRM, billing | The entity that pays |
| Subscription | Billing system | The recurring revenue unit |
| Product / Module | Product catalog | What's being sold |
| Feature | Product data, usage logs | Sub-product capability |
| Ticket / Issue | Support system | Customer interaction unit |
| Deployment / Instance | Infrastructure data | Per-customer technical footprint |

## Key Relationships

- **subscribes_to** (Customer → Product): What they're paying for
- **uses** (Customer → Feature): What they actually use
- **owns** (Employee → Customer): Account ownership (CS/Sales)
- **filed_by** (Ticket → Customer): Support attribution
- **depends_on** (Product → Product): Platform dependencies

## Domain Concepts

- **ARR / MRR**: Annual/Monthly Recurring Revenue. The core metric.
- **Churn**: Customer or revenue loss rate. Gross vs. net.
- **NRR / NDR**: Net Revenue Retention / Net Dollar Retention. Expansion minus contraction.
- **ACV**: Annual Contract Value.
- **LTV**: Lifetime Value. Usually LTV = ACV / churn rate.
- **CAC**: Customer Acquisition Cost.
- **Cohort**: Customers grouped by signup date for retention analysis.

## Behavioral Properties for Simulation

- **Logo churn risk**: Based on usage decline, support ticket sentiment, contract renewal date
- **Expansion potential**: Based on usage growth, feature adoption, seat utilization
- **Key account dependency**: Revenue concentration in top accounts
- **Engineering capacity**: Velocity, tech debt ratio, deployment frequency
- **Sales efficiency**: CAC payback period, quota attainment distribution
