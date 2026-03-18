# builder-testdata

Generates 2 years of realistic operational data for a $1M-$3M trade/general contractor business. Designed to power development and testing of AI administrative assistants, estimating tools, and job costing systems.

## What it generates

With default settings (seed 42, 2024-2025):

| Entity | Count | Notes |
|--------|-------|-------|
| Projects | ~65 | Across 6 archetypes |
| Estimates (inc. lost) | ~103 | 63% win rate |
| Jobs (cost codes) | ~376 | 5-19 phases per project |
| Time entries | ~2,300 | Daily crew hours by job |
| Bills | ~968 | Materials + subs + overhead |
| Invoices | ~176 | Progress + final + retention |
| Payments | ~176 | With realistic lag |
| Customers | 13 | Residential + commercial |
| Vendors | 10 | Suppliers + subs |
| Employees | 5-9 | Crew changes over time |

**~$2.5M total billed over 2 years.** Gross margin ~25-35% depending on seed.

## The business narrative

The generator models **Ridgeline Builders** — a general contractor based in central PA. The data follows a coherent business story, not random noise:

- **Seasonal rhythm**: estimating peak in winter, execution peak May-August
- **Growing revenue**: ~$1.4M in 2024, ~$1.9M in 2025
- **Real problems**: late payments, budget overruns from unforeseen conditions, a sub no-showing, a key employee leaving mid-peak season, weather delays
- **Business evolution**: crew additions, a promotion, pricing adjustments, a first new-construction job, adding an office admin

Key narrative events injected into the data:
- Johnson kitchen payment 45 days late — forces a line-of-credit draw
- Morrison addition hits rock — $8,200 overrun, only $4,000 CO approved
- Apex Electrical no-show — 6-day delay, $2,100 eaten
- Carlos Vega leaves for union — 6 weeks of overtime coverage
- Owner raises T&M rate from $85 to $110/hr (visible in service call margins)

## Quick start

```bash
pip install -r requirements.txt
python generate.py
```

Output goes to `./output/`:
- `data.json` — all entities in one file
- `csv/` — one CSV per entity type
- `builder.db` — SQLite database

## Options

```bash
python generate.py --seed 42              # reproducible (same seed = same data)
python generate.py --start 2024-01-01 --end 2025-12-31
python generate.py --format json          # json | csv | sqlite | all (default)
python generate.py --out ./my-output
python generate.py --summary              # print stats (default: on)
```

## Configuring the business

Everything is driven by three YAML files in `config/`:

| File | Controls |
|------|---------|
| `company.yaml` | Company name, crew roster + timeline, vendors, financials, win rates |
| `archetypes.yaml` | Project types, phase structures, cost/price ranges, customer pool |
| `events.yaml` | Named narrative events + recurring overhead bills |

To generate a different builder (electrician, plumber, roofing company):
1. Edit `config/company.yaml` — change trades, crew roles, bill rates
2. Edit `config/archetypes.yaml` — add/remove archetypes, adjust phase structures
3. Edit `config/events.yaml` — swap or add narrative events

## Data model

The ontology follows standard construction job costing:

```
Customer
  └── Estimate (bid)
        └── EstimateLineItem
        └── Project (if won)
              └── Job (cost code / phase)
                    └── TimeEntry (labor actuals)
                    └── BillLineItem (material/sub actuals)
              └── ChangeOrder
              └── Invoice
                    └── Payment
Vendor
  └── Bill
        └── BillLineItem
```

**Profitability at every level:**
- Per-job: `budgeted_*_cost` vs sum of actual `time_entry.cost` + `bill_line_item.line_total`
- Per-project: `contract_amount` + approved change orders vs sum of job actuals
- Per-period: total invoiced vs total costs + overhead

## Project archetypes

| Archetype | Typical range | Margin | Duration |
|-----------|--------------|--------|----------|
| Kitchen remodel | $38K-$125K | 28-40% | 6-10 wk |
| Bathroom remodel | $12K-$52K | 30-44% | 3-6 wk |
| Deck / outdoor structure | $18K-$75K | 32-44% | 3-7 wk |
| Room addition | $65K-$220K | 24-36% | 8-20 wk |
| New construction | $280K-$620K | 16-26% | 18-40 wk |
| Repair / service call | $350-$6,500 | 45-68% | days |
| Commercial TI | $35K-$210K | 20-32% | 5-14 wk |

## Design notes

**Coherence constraints** — the generator enforces:
- Cash approximately balances (revenue ≈ costs + margin)
- Crew capacity limits concurrent project execution
- Materials arrive before labor that uses them
- Invoices track against contract value + change orders
- Seasonal patterns are consistent year-over-year but not identical

**Variance is intentional** — some jobs run over budget, some under, some customers pay late. This is what an AI assistant needs to learn to detect.

**Reproducible** — pass `--seed N` to get identical output. Useful for regression testing against a known dataset.
