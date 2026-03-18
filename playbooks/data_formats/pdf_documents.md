# PDF Documents

## Document Types in Data Rooms

Common PDF types and what to extract from each:

| Type | Entity Signals | Relationship Signals |
|------|---------------|---------------------|
| Org charts | People, departments, roles | Reporting relationships |
| Financial reports | Accounts, segments, periods | Revenue/cost allocation |
| Board decks | Initiatives, KPIs, people | Ownership, status, timelines |
| Contracts | Parties, terms, provisions | Contractual relationships |
| Audit reports | Findings, entities, controls | Control ownership, exceptions |

## Table Detection

PDFs with tables are valuable but hard to parse. Strategies:

1. **Structured tables**: Regular grid layout with clear borders. Tools like
   `tabula-py` or `camelot` can extract these reliably.
2. **Semi-structured**: Aligned text without borders. Look for consistent
   column spacing.
3. **Embedded images**: Tables that are actually images (scanned docs).
   Requires OCR first.

For Phase 0, don't attempt table extraction. Note the document type,
estimated table count, and flag for potential extraction in Phase 2.

## Entity Mention Extraction

From narrative PDFs (board decks, memos, reports), extract:

- **People names**: Titles, roles, departments mentioned alongside names
- **Organization names**: Subsidiaries, divisions, external entities
- **Financial figures**: Revenue, cost, EBITDA, headcount numbers
- **Dates and timelines**: Periods, deadlines, milestone dates
- **Contract references**: Agreement names, counterparties, terms

These mentions become evidence for entity types and relationships
discovered in Phase 1.

## Scanned vs. Digital PDFs

- **Digital (text-selectable)**: Text can be extracted directly
- **Scanned (image-based)**: Requires OCR before text extraction
- **Mixed**: Some pages digital, some scanned (common in data rooms
  where documents from different sources are combined)

For Phase 0, classify each PDF as digital, scanned, or mixed.
Scanned PDFs should be flagged as lower confidence sources.
