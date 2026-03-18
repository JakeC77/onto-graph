# Delivery Manifest — Ridgeline Builders

**Run ID:** ridgeline_20260318
**Company:** Ridgeline Builders
**Generated:** 2026-03-18

## Artifacts

### Phase 0: Catalog
| File | Description |
|------|-------------|
| `phase_0_catalog/data_catalog.yaml` | Complete inventory of 18 data sources with statistical profiles, join candidates, and candidate entity types |
| `phase_0_catalog/source_profiles/` | 16 individual source profile YAMLs |

### Phase 1: Ontology
| File | Description |
|------|-------------|
| `phase_1_ontology/ontology.yaml` | 14 entity types, 14 relationships, 10 domain concepts |
| `phase_1_ontology/decisions/D_1001.yaml` | Vendor: single type vs. split Supplier/Subcontractor |
| `phase_1_ontology/decisions/D_1002.yaml` | NarrativeEvent: single type vs. separate per event kind |
| `phase_1_ontology/decisions/D_1003.yaml` | BillLineItem: separate entity type vs. collapse into Bill |
| `phase_1_ontology/decisions/D_1004.yaml` | EstimateLineItem to Job mapping via cost_code |

### Phase 2: Mapping
| File | Description |
|------|-------------|
| `phase_2_mapping/mapping_plan.yaml` | 168 field mappings, 14 relationship mappings, 6 statistical computations. Coverage: 100% |
| `phase_2_mapping/decisions/D_2001.yaml` | Single-source conflict resolution strategy |
| `phase_2_mapping/decisions/D_2002.yaml` | Statistical computation window choices |

### Phase 3: Architecture
| File | Description |
|------|-------------|
| `phase_3_architecture/etl_architecture.yaml` | 9-stage pipeline DAG, 16 source pipeline specs, Neo4j schema |
| `phase_3_architecture/neo4j_schema.cypher` | Cypher DDL: 14 constraints, 46 indexes |
| `phase_3_architecture/decisions/D_3001.yaml` | MERGE upsert strategy for all entities |
| `phase_3_architecture/decisions/D_3002.yaml` | Entities-before-relationships pipeline ordering |
| `phase_3_architecture/decisions/D_3003.yaml` | neo4j_direct over SDG CSV export |

### Delivery
| File | Description |
|------|-------------|
| `delivery/ontology_document.md` | Human-readable ontology reference |
| `delivery/mapping_document.md` | Human-readable mapping plan reference |
| `delivery/architecture_document.md` | Human-readable ETL architecture reference |
| `delivery/delivery_manifest.md` | This file |

## Summary

- **Entity Types:** 14 (Company, Customer, Vendor, Employee, Estimate, EstimateLineItem, Project, Job, TimeEntry, Bill, BillLineItem, Invoice, Payment, NarrativeEvent)
- **Relationships:** 14
- **Domain Concepts:** 10
- **Decision Records:** 9 (D_1001-D_1004, D_2001-D_2002, D_3001-D_3003)
- **Field Mappings:** 168 (100% coverage)
- **Source Utilization:** 16/18 consumed (2 excluded as alternate formats)
- **Pipeline Stages:** 9
- **Neo4j Constraints:** 14
- **Neo4j Indexes:** 46
