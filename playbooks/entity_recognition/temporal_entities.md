# Temporal Entities

## Entity Types

### Period

**Signals in data:**
- Columns: fiscal_year, quarter, month, period_id, reporting_period
- Properties: start_date, end_date, period_type, fiscal_year_offset
- Appears in: financial data, performance data, planning data

**Entity vs. property test:** If periods are referenced by multiple entity types
(financials by period, headcount by period, initiatives by period) and have
their own properties (open/closed, adjusted) → entity type. If dates are
just columns on other entities → properties.

Most financial and operational data is period-dimensioned. Modeling Period
as an entity type enables time-series analysis across all entity types.

### Event

**Signals in data:**
- Columns: event_id, event_type, event_date, event_name
- Properties: type, date, participants, outcome, impact
- Appears in: audit logs, change logs, transaction histories

**Common confusion:**
- Event vs. Transaction: Transactions are financial events. If transactions
  have their own entity lifecycle (pending → completed → reconciled) they
  may warrant their own entity type.
- Event vs. State Change: Some "events" are just state transitions on other
  entities (employee promoted, contract renewed). These are better modeled as
  properties with timestamps on the parent entity.

**When Event is an entity type:**
- Events are independently queryable (audit trail requirements)
- Events connect multiple entity types (a departure event involves a Person,
  their Department, and their open Initiatives)
- Event patterns are analytically important (clustering, frequency, sequence)

### Milestone

**Signals in data:**
- Columns: milestone_id, milestone_name, target_date, actual_date
- Properties: status, owner, initiative, dependencies
- Appears in: project plans, timelines, board presentations

**Entity vs. property test:** If milestones are tracked with their own
dependencies, ownership, and slippage → entity type. If they're just
dates on an initiative → properties.

## Temporal Patterns to Watch For

### Timeline Sequences
Multiple related events with a defined order:
- Carveout timeline: separation → TSA start → system migration → TSA end
- Initiative lifecycle: ideation → approval → execution → completion
- Contract lifecycle: negotiation → execution → performance → renewal/termination

If the sequence itself is analytically important, model it explicitly
(either as a relationship chain or as a Timeline entity type).

### Temporal Joins
Different entity types measured at different temporal grains:
- Financial data: monthly
- Headcount data: point-in-time snapshots (monthly or quarterly)
- Contract data: event-driven (no regular grain)
- Initiative data: weekly or biweekly status updates

Note the temporal grain mismatch. Phase 2 will need to specify how to
align different grains for cross-entity analysis.

## Red Flags

- **Fiscal vs. calendar mismatch**: Different sources using different year boundaries
- **Missing timestamps**: Entity data without creation or modification dates
- **Future-dated records**: Data points dated in the future (plans, forecasts mixed with actuals)
- **Timezone ambiguity**: Dates without timezone info when sources span regions
