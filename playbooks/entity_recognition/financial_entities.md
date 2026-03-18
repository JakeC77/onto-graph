# Financial Entities

## Entity Types

### Account

**Signals in data:**
- Columns: account_id, account_number, gl_account, account_name
- Hierarchical: accounts roll up (expense → COGS → total expenses)
- Properties: account_type (asset, liability, equity, revenue, expense), balance

**Common confusion:**
- Account vs. Cost Center: Accounts are financial classification (what);
  cost centers are organizational allocation (who pays). Both exist as entity
  types if they have independent properties and relationships.
- Account vs. Line Item: A line item is a transaction on an account.
  Accounts persist; line items are events.

### CostCenter

**Signals in data:**
- Columns: cost_center, cc_id, cost_center_name, responsibility_center
- Usually maps to organizational units but not 1:1
- May have: manager, budget, actual spend

**Entity vs. property test:** If cost centers have their own budget, manager,
and hierarchy → entity type. If they're just department aliases → property.

### RevenueSegment

**Signals in data:**
- Columns: segment, business_line, revenue_category, product_line
- Appears in: P&L data, revenue reports, customer contract data
- Properties: description, target, actual

**Common confusion:**
- Revenue segment vs. Department: Segments are market-facing; departments are
  internal. A segment might span multiple departments.
- Revenue segment vs. Product: Products generate revenue in segments.
  If both have independent properties → separate types.

### Budget

**Signals in data:**
- Columns: budget_id, fiscal_year, budget_amount, budget_category
- Usually periodic (annual, quarterly)
- Relationships: allocated_to (Department, CostCenter, Initiative)

**Entity vs. property test:** If budgets have their own lifecycle (draft → approved → revised)
and versioning → entity type. If it's just a number on a department → property.

## Financial Hierarchy Patterns

Financial data typically has multiple hierarchies:

1. **Chart of accounts**: Account → Sub-account → GL line
2. **Cost allocation**: Cost center → Department → Division
3. **Revenue rollup**: Product → Segment → Business line
4. **Budget hierarchy**: Line item → Category → Total

## Temporal Dimension

Financial entities are almost always time-dimensioned:
- **Balance sheet items**: Point-in-time snapshots
- **P&L items**: Period-based (monthly, quarterly, annual)
- **Budgets**: Fiscal year/quarter with versions

Note the temporal grain in the profile. Financial entity types may need
a Period dimension to be properly modeled.

## Red Flags

- **No chart of accounts**: Financial data without account hierarchy → limited analysis
- **Mixed currencies**: Multiple currencies without conversion rates
- **Fiscal vs. calendar year mismatch**: Data from different sources using different year-ends
- **Intercompany transactions**: Transactions between related entities that inflate totals
