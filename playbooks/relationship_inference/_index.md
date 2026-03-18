# Relationship Inference — Playbook Index

Patterns and methods for discovering relationships between entity types.
Use during Phase 1 (Ontology Discovery) when analyzing how entities connect.

## When to Load

Load specific skills based on the type of evidence available in the data.
Start with structural relationships (explicit in tabular data), then move
to behavioral and inferred relationships if the data supports them.

## Skills

| Skill | Evidence Type | Confidence |
|-------|-------------|-----------|
| `structural_relationships.md` | Explicit FK/PK links, hierarchy columns | High |
| `behavioral_relationships.md` | Communication data, approval logs, activity patterns | Medium |
| `financial_relationships.md` | Cost allocation, revenue flows, budget linkages | High |
| `contractual_relationships.md` | Party-to-contract, provisions, guarantees | High |
| `statistical_relationships.md` | Correlation, co-occurrence, temporal patterns | Low-Medium |

## Discovery Order

1. **Structural first**: FK/PK joins from Phase 0 join candidates → highest confidence
2. **Financial second**: Follow the money — cost allocation and revenue flows
3. **Contractual third**: Legal relationships between parties
4. **Behavioral fourth**: Communication and activity patterns (if data exists)
5. **Statistical last**: Correlation-based inference (lowest confidence, most speculative)

## Routing

- **Join candidates with high overlap?** → `structural_relationships.md`
- **GL or cost allocation data?** → `financial_relationships.md`
- **Contract/party data?** → `contractual_relationships.md`
- **Email/communication/approval logs?** → `behavioral_relationships.md`
- **No explicit links but entities co-occur?** → `statistical_relationships.md`
