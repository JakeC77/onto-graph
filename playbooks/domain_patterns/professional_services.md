# Professional Services

Common ontology patterns for consulting firms, law firms, staffing agencies,
and other people-centric service businesses.

## Typical Entity Types

| Entity Type | Signals | Notes |
|------------|---------|-------|
| Employee | Standard HR data | The core entity — people ARE the product |
| Practice / Service Line | Revenue segmentation | How the firm organizes expertise |
| Client | CRM data, billing data | External organizations buying services |
| Engagement / Matter | Project tracking, billing | A bounded piece of work for a client |
| Timesheet Entry | Time tracking system | The raw unit of revenue measurement |
| Rate Card | Pricing data | Billing rates by role/level/client |
| Skill / Certification | HR or capability data | What people can do |

## Key Relationships

- **staffed_on** (Employee → Engagement): Who works on what
- **billed_to** (Engagement → Client): Revenue attribution
- **belongs_to** (Employee → Practice): Organizational home
- **has_skill** (Employee → Skill): Capability mapping
- **priced_at** (Role/Level × Client → Rate): Billing rate determination

## Domain Concepts

- **Utilization**: Billable hours / available hours. The core performance metric.
- **Realization**: Actual billed amount / standard rate. How much of the rate card is captured.
- **Leverage**: Ratio of junior to senior staff. Drives profitability.
- **Backlog**: Contracted but undelivered work.
- **Pipeline**: Prospective work at various probability stages.

## Behavioral Properties for Simulation

- **Client concentration**: Revenue from top clients / total revenue
- **Key person dependency**: Revenue attributed to specific individuals
- **Bench time**: Unstaffed capacity (cost without revenue)
- **Attrition risk**: Based on utilization, tenure, compensation equity
