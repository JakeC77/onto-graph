# Behavioral Relationships

Relationships inferred from patterns of activity, communication, and interaction.
Medium confidence — supported by data but requires interpretation.

## When This Applies

Behavioral relationships require activity data:
- Email/messaging logs (sender, recipient, timestamp)
- Approval chains (who approves what, how often)
- Meeting data (attendees, frequency, duration)
- Collaboration signals (co-editing, shared files, co-assigned tasks)
- Access logs (who accesses which systems, how often)

If the data room has no activity data, skip this skill.

## Communication Relationships

From email/messaging data:

- **communicates_with** (Person ↔ Person): Frequency of direct communication
  - Properties: frequency, avg_response_time, reciprocity_ratio
  - Confidence: High for frequent pairs, low for one-off exchanges
  - Threshold: Define "significant" communication (e.g., > 5 exchanges/month)

- **Informal reporting**: Communication patterns may reveal actual
  (vs. formal) reporting relationships. If Person A communicates heavily
  with Person B despite no formal reports_to link → note as a behavioral
  relationship.

## Approval Relationships

From approval/workflow logs:

- **approves** (Person → various): Who approves what
  - Properties: frequency, approval_type, avg_time_to_decision
  - Entity types approved: expenses, initiatives, contracts, hires

- **Delegation patterns**: If Person A's approvals are consistently
  performed by Person B → delegation relationship

## Collaboration Relationships

From co-activity patterns:

- **collaborates_with** (Person ↔ Person): Based on shared activities
  - Co-assigned to same initiatives
  - Co-attending meetings
  - Co-editing documents
  - Properties: overlap_count, collaboration_type

- **Cross-functional links**: People in different departments who
  collaborate frequently → these are often organizationally important

## Inference Rules

1. **Frequency threshold**: Set a minimum to avoid noise. A single email
   is not a relationship. 5+ interactions/month over 3+ months is.
2. **Reciprocity**: One-way communication (person A emails B but never
   gets replies) is different from two-way. Note the directionality.
3. **Temporal stability**: Relationships that persist over time are more
   meaningful than bursts of activity.
4. **Context**: Communication during a crisis/project is situational,
   not structural. Check if patterns persist outside specific events.

## For Simulation

Behavioral relationships feed directly into Simulation's constraint profiles:
- Communication density → influence propagation
- Approval patterns → decision authority
- Collaboration patterns → knowledge distribution

Note these as computed properties in the ontology for Phase 2 mapping.
