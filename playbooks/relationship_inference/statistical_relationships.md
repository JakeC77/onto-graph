# Statistical Relationships

Relationships inferred from patterns, correlations, and co-occurrence in data.
Lowest confidence of all discovery methods — use when structural and behavioral
evidence is unavailable.

## When This Applies

Use statistical methods when:
- No explicit FK/join keys connect two entity types
- No behavioral data (communication, activity) exists
- But entities co-occur in patterns that suggest a relationship

## Co-occurrence Analysis

Entities that frequently appear together may be related:

- **Same-row co-occurrence**: If Person A and Initiative X appear in the
  same row across multiple sources → likely A is involved with X
  - Confidence: Medium (depends on frequency and exclusivity)
  - Minimum threshold: 3+ independent co-occurrences

- **Same-document co-occurrence**: Entities mentioned in the same document
  are weakly related (they're in the same context)
  - Confidence: Low (proximity ≠ relationship)
  - Only upgrade if the co-occurrence is specific (not a company-wide doc)

- **Temporal co-occurrence**: Events/changes happening to both entities at
  the same time suggest coupling
  - Confidence: Medium (coincidence is possible)
  - Stronger if the temporal pattern repeats

## Correlation-Based Relationships

When quantitative data exists for two entity types:

- **Metric correlation**: If Department A's headcount changes correlate with
  Initiative X's spending → resource dependency
  - Method: Pearson/Spearman correlation on time-series data
  - Threshold: |r| > 0.7 and p < 0.05 for medium confidence

- **Behavioral correlation**: If Person A's activity level correlates with
  Person B's → possible collaboration or dependency
  - Requires activity/communication data
  - Normalize for overall activity levels (don't just find busy people)

## Network Inference

From known relationships, infer missing ones:

- **Transitive closure**: If A reports_to B and B reports_to C, then A is
  (transitively) under C. This is structural, not inferred.
- **Common neighbor**: If A and B both relate to C but have no direct
  relationship, they may be indirectly connected.
  - Useful for: finding implicit collaboration, shared dependencies
  - Confidence: Low (common neighbor ≠ direct relationship)

## Patterns That Suggest Relationships

| Pattern | Suggested Relationship | Confidence |
|---------|----------------------|-----------|
| Two entity types always change at the same time | Dependency or coupling | Medium |
| One entity type's metric predicts another's | Causal or correlated | Medium |
| Entity types share the same dimension values | Same organizational context | Low |
| Entity types referenced in same narrative | Contextual relationship | Low |
| Removal of one entity impacts another's metrics | Functional dependency | Medium-High |

## Confidence Calibration

Statistical relationships should be tagged with:
- **Method**: What statistical method was used
- **Sample size**: How much data supports the inference
- **Effect size**: How strong is the signal
- **Confounders**: What other explanations exist

Always present statistical relationships alongside their evidence.
Phase 2 can decide whether to include them in the mapping.

## For Simulation

Statistical relationships are especially valuable for Simulation because
they reveal hidden coupling. But their lower confidence means:
- They should be flagged as "inferred" in the ontology
- They should have wider uncertainty bounds in the mapping plan
- Simulation can still use them but with appropriate confidence weights
