# BOH Agent for Small Builders (1-3M Revenue)

## Vision

A back-of-house (BOH) personal assistant for small general contractors and
trade businesses doing $1-3M in annual revenue. The agent handles scheduling,
project management, basic finances, estimating, and operational coordination —
powered by a live knowledge graph that understands the builder's business as a
connected whole, not as siloed spreadsheets.

The target user is a builder who currently runs their business from a mix of
QuickBooks, a PM tool (or spreadsheets), a phone, and their head. They don't
have a full-time office manager. The BOH agent is that office manager.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Agent                         │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │Scheduling│  │ Project  │  │ Finance  │  │ Estimating │  │
│  │  Skills  │  │   Mgmt   │  │  Skills  │  │   Skills   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │              │             │               │         │
│       └──────────────┴──────┬──────┴───────────────┘         │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │  Graph Query    │                       │
│                    │    Layer        │                       │
│                    └────────┬────────┘                       │
└─────────────────────────────┼───────────────────────────────┘
                              │
                     ┌────────▼────────┐
                     │    Neo4j        │
                     │  Knowledge      │
                     │    Graph        │
                     └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
     │  ETL Pipeline │ │  ETL       │ │  ETL         │
     │  (Accounting) │ │  (PM/Sched)│ │  (Field Data)│
     └────────┬──────┘ └─────┬──────┘ └──────┬───────┘
              │               │               │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
     │  QuickBooks   │ │  Procore / │ │  Timesheets  │
     │  / Xero       │ │ Buildertrend│ │  / Photos   │
     └───────────────┘ └────────────┘ └──────────────┘
```

---

## How the Pieces Fit Together

### 1. Data Generator → Realistic Test Bed

The `builder-data/` generator creates a full 2-year dataset for a company
matching the target profile (Ridgeline Builders: ~$1.4-1.9M revenue, 5-9
employees, residential + light commercial GC work). It produces:

- **65 projects** across 7 archetypes (kitchen, bath, deck, addition, new
  construction, repair, commercial TI)
- **2,300 time entries**, **968 bills**, **176 invoices/payments**
- **Narrative events** baked in: late-paying customers, cost overruns,
  subcontractor insurance lapses, weather delays, new hires

This is the development and demo dataset. Every BOH agent capability gets built
and tested against this data first. When we onboard a real builder, their actual
data replaces it — but the shape is the same.

**Role in the stack:** The generator produces the raw data room that feeds
Ontograph. It also seeds the Neo4j graph for agent development, so we can build
and test agent skills against a realistic business without needing a live
customer.

### 2. Ontograph → Automated Schema Discovery & Graph Standup

Ontograph is the bridge between raw business data and a typed knowledge graph.
For each new builder onboarding, it runs a 5-phase pipeline:

| Phase | What it does | Why it matters for BOH |
|-------|-------------|----------------------|
| **0. Catalog** | Inventories all data sources, profiles columns, detects joins | Tells us what data the builder actually has and how it connects |
| **1. Ontology** | Discovers entity types (Project, Customer, Vendor, Employee, Invoice...) and relationships from the data | Builds the graph schema that the agent queries against |
| **2. Mapping** | Maps every field to the ontology with transformations | Defines exactly how QuickBooks exports become graph nodes |
| **3. Architecture** | Designs ETL pipelines, generates Neo4j Cypher DDL | Produces the runnable infrastructure to populate the graph |
| **4. Deliver** | Renders human-readable docs | Gives the builder (and us) a clear picture of their data model |

**Role in the stack:** Ontograph is the onboarding engine. When a new builder
signs up, we point it at their data exports and it produces everything needed to
stand up their graph — no manual schema design required. This is what makes the
system work for small builders who can't afford a data engineering engagement.

### 3. Neo4j Knowledge Graph → The Agent's Brain

The graph produced by Ontograph becomes the agent's working memory. Instead of
querying flat tables, the agent traverses a connected graph where:

```
(Customer)-[:HAS_PROJECT]->(Project)-[:HAS_JOB]->(Job)
(Job)-[:HAS_TIME_ENTRY]->(TimeEntry)-[:BY_EMPLOYEE]->(Employee)
(Project)-[:HAS_INVOICE]->(Invoice)-[:HAS_PAYMENT]->(Payment)
(Project)-[:HAS_CHANGE_ORDER]->(ChangeOrder)
(Vendor)-[:SUPPLIED]->(BillLineItem)-[:FOR_JOB]->(Job)
```

This structure lets the agent answer questions that would require joining 5+
tables in a relational database — naturally and fast.

### 4. OpenClaw Agent → The Interface

The OpenClaw subagent sits on top of the graph and provides the builder with a
conversational (and eventually proactive) assistant. Its skill domains:

#### Scheduling & Resource Management
- "Who's free next week?"
- "Can we start the Morrison kitchen on the 15th?"
- "Luis has been on the Sutton job for 6 weeks — who can rotate in?"
- Conflict detection across crew assignments
- Subcontractor availability tracking

#### Project Management
- Project status dashboards (% complete by cost, not just time)
- Change order tracking and margin impact
- Punchlist and completion tracking
- "Which projects are behind schedule?"
- "What's the status on the Park bathroom?"

#### Financial Operations
- Cash flow forecasting (invoices outstanding vs. bills due)
- Job costing (actual vs. estimate by cost code)
- "Who owes us money?" / "What bills are due this week?"
- Margin alerts (project trending below target)
- Draw schedule tracking for larger projects
- "How did we do on kitchens this year vs last year?"

#### Estimating Support
- Pull historical job costs by project archetype
- "What did framing cost us per sqft on the last 3 additions?"
- Template-based estimate generation with actual cost data
- Material price trend tracking (via vendor bill history)

#### Proactive Alerts
- Subcontractor COI expirations approaching
- Customer payment aging past threshold
- Project margin dropping below archetype target
- Crew utilization imbalances
- Cash flow pinch points (big bills due, receivables lagging)

---

## Onboarding Flow (New Builder)

```
1. Builder signs up
   │
2. Export data from their systems
   │  (QuickBooks backup, PM export, crew spreadsheets)
   │
3. Data lands in data room
   │  data/{company}/data_room/
   │
4. Engagement brief created
   │  (systems, data room path, context)
   │
5. Ontograph runs Phases 0-4
   │  ├── Discovers their specific schema
   │  ├── Generates Neo4j DDL
   │  └── Produces ETL pipeline specs
   │
6. ETL pipeline executes
   │  (populates Neo4j from their data)
   │
7. OpenClaw agent connects to their graph
   │
8. Builder starts asking questions
```

For the target market (1-3M builders), the data landscape is predictable enough
that Ontograph's playbooks handle most of it automatically:

- **Accounting:** QuickBooks (90%+ of this market), Xero, or Sage
- **PM:** Buildertrend, Procore, CoConstruct, or spreadsheets
- **Time tracking:** Built into PM tool, T-Sheets, or paper → spreadsheet
- **Estimating:** Spreadsheets, or built into PM tool

The system schema playbooks (`playbooks/system_schemas/`) already contain
recognition patterns for QuickBooks, Procore, Buildertrend, and others common
in this market.

---

## Why a Graph (Not Just a Database)

Small builders' data is inherently relational in ways that spreadsheets and even
relational databases make hard to query:

| Question | Relational (SQL) | Graph (Cypher) |
|----------|-----------------|----------------|
| "Which subs worked on projects that went over budget?" | 3-4 JOINs across bills, jobs, projects, estimates | Single traversal |
| "Show me all the people and costs connected to the Morrison job" | Multiple queries stitched together | `(p:Project {name:'Morrison'})-[*1..3]-()` |
| "What's the chain from this invoice to the original estimate line?" | Recursive CTEs or application logic | Path query |

The graph also enables the agent to discover patterns the builder hasn't asked
about — cost overrun correlations with specific subs, seasonal cash flow
patterns, crew productivity variations by project type.

---

## Development Phases

### Phase 1: Core Loop (MVP)
- Data generator producing test dataset
- Ontograph pipeline running against generated data
- Neo4j populated with builder graph
- OpenClaw agent with basic query skills (project status, financials, crew)
- Single-tenant, demo-only

### Phase 2: Real Data
- Onboard 1-2 pilot builders
- Ontograph runs against real exports (QuickBooks + PM tool)
- ETL pipeline runs on schedule (weekly batch refresh)
- Agent handles day-to-day queries
- Feedback loop: agent gaps → ontology refinement

### Phase 3: Proactive & Write-Back
- Agent generates alerts and recommendations unprompted
- Write-back to source systems (create invoices, schedule entries)
- Mobile-friendly interface for field use
- Multi-tenant infrastructure

### Phase 4: Market
- Self-serve onboarding (guided data export + Ontograph auto-run)
- Integration connectors (QuickBooks API, Procore API) replacing file exports
- Estimating module with historical cost intelligence
- Builder-to-builder benchmarking (anonymized)

---

## Technical Stack (Proposed)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Agent runtime | OpenClaw | Subagent architecture, skill-based |
| Knowledge graph | Neo4j | Cypher queries, schema from Ontograph |
| Schema discovery | Ontograph | This repo — phases 0-4 |
| Test data | builder-data generator | This repo — `builder-data/` |
| ETL | Python scripts | Generated by Ontograph Phase 3 |
| Source integrations | QuickBooks API, file imports | Phase 2-3 adds live connectors |
| Interface | Chat (OpenClaw native) | Eventually: mobile, voice |

---

## Key Insight

The combination of Ontograph + Data Generator solves the cold-start problem for
vertical AI agents:

- **Data Generator** gives us a realistic, narrative-rich dataset to develop
  against without waiting for customer data
- **Ontograph** automates the hardest part of onboarding — understanding a new
  builder's data landscape and standing up their graph — so we don't need a data
  engineer per customer
- **The graph** gives the agent connected context that makes it actually useful,
  not just a chatbot wrapper around flat queries

For a 1-3M builder, the BOH agent replaces the part-time bookkeeper, the PM
tool they never fully adopted, and the spreadsheets they maintain in their truck.
It's the office they can't afford to staff.
