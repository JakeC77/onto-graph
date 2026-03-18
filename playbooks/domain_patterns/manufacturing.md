# Manufacturing

Common ontology patterns for manufacturing, distribution, and logistics businesses.

## Typical Entity Types

| Entity Type | Signals | Notes |
|------------|---------|-------|
| Employee | HR data | Includes production, engineering, logistics |
| Product / SKU | Product master data | Finished goods |
| Component / Material | BOM data | Inputs to production |
| Supplier / Vendor | Procurement data | Who provides materials |
| Customer | Sales/order data | Who buys products |
| Work Order | Production system | A production run |
| Facility / Plant | Location data | Where production happens |
| Equipment / Machine | Asset data | Production equipment |
| Warehouse / Location | Inventory system | Where things are stored |

## Key Relationships

- **bill_of_materials** (Product → Component): What goes into what
- **supplies** (Vendor → Component): Who provides materials
- **produced_at** (Product → Facility): Where products are made
- **stored_at** (Product → Warehouse): Inventory location
- **routed_through** (Work Order → Equipment): Production routing
- **ordered_by** (Order → Customer): Sales relationship

## Domain Concepts

- **BOM (Bill of Materials)**: Hierarchical — finished good → sub-assemblies → raw materials
- **Routing**: Sequence of operations/machines needed to produce a product
- **Lead time**: Time from order to delivery
- **Yield**: Good units / total units produced
- **OEE**: Overall Equipment Effectiveness (availability × performance × quality)
- **Safety stock**: Minimum inventory to buffer demand variability
- **MOQ**: Minimum Order Quantity from suppliers

## Behavioral Properties for Simulation

- **Supplier concentration**: Single-source components create dependency risk
- **Equipment criticality**: Machines with no backup and high utilization
- **Inventory turns**: Working capital efficiency signal
- **Quality trends**: Defect rates by product, line, or shift
- **Capacity utilization**: Actual vs. maximum production volume
