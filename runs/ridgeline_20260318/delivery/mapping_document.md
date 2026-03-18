# Data Mapping Plan — Ridgeline Builders

Generated from `runs/ridgeline_20260318/phase_2_mapping/mapping_plan.yaml` on 2026-03-18

## Coverage Summary

- **Properties mapped:** 168
- **Properties gapped:** 0
- **Coverage rate:** 100%
- **Entity mappings:** 14
- **Relationship mappings:** 14
- **Statistical computations:** 6

## Entity Mappings

### Company

- **System of record:** `381f49880b21`
- **Merge key:** `name`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `name` | `381f49880b21` | `name` | none | skip |
| `trade` | `381f49880b21` | `trade` | none | skip |
| `region` | `381f49880b21` | `region` | none | skip |
| `owner_name` | `381f49880b21` | `owner_name` | none | skip |
| `owner_employee_id` | `381f49880b21` | `owner_employee_id` | none | skip |
| `address` | `381f49880b21` | `address` | none | skip |
| `phone` | `381f49880b21` | `phone` | none | skip |
| `email` | `381f49880b21` | `email` | none | skip |
| `license_number` | `381f49880b21` | `license_number` | none | skip |

### Customer

- **System of record:** `dab846594bbb`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `dab846594bbb` | `id` | none | skip |
| `name` | `dab846594bbb` | `name` | none | skip |
| `email` | `dab846594bbb` | `email` | none | skip |
| `phone` | `dab846594bbb` | `phone` | none | skip |
| `address` | `dab846594bbb` | `address` | none | skip |
| `payment_terms` | `dab846594bbb` | `payment_terms` | normalize | skip |
| `source` | `dab846594bbb` | `source` | normalize | skip |
| `type` | `dab846594bbb` | `type` | normalize | skip |
| `tax_exempt` | `dab846594bbb` | `tax_exempt` | cast | default |
| `credit_limit` | `dab846594bbb` | `credit_limit` | cast | default |
| `status` | `dab846594bbb` | `status` | none | skip |
| `created_at` | `dab846594bbb` | `created_at` | cast | skip |
| `notes` | `dab846594bbb` | `notes` | none | default |

### Vendor

- **System of record:** `580ea3721ca9`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `580ea3721ca9` | `id` | none | skip |
| `name` | `580ea3721ca9` | `name` | none | skip |
| `type` | `580ea3721ca9` | `type` | normalize | skip |
| `trade` | `580ea3721ca9` | `trade` | none | default |
| `contact` | `580ea3721ca9` | `contact` | none | default |
| `phone` | `580ea3721ca9` | `phone` | none | default |
| `email` | `580ea3721ca9` | `email` | none | default |
| `payment_terms` | `580ea3721ca9` | `payment_terms` | normalize | skip |
| `tax_id` | `580ea3721ca9` | `tax_id` | none | default |
| `w9_on_file` | `580ea3721ca9` | `w9_on_file` | cast | default |
| `insurance_expiry` | `580ea3721ca9` | `insurance_expiry` | cast | default |
| `rating` | `580ea3721ca9` | `rating` | cast | default |
| `credit_limit` | `580ea3721ca9` | `credit_limit` | cast | default |
| `account_opened` | `580ea3721ca9` | `account_opened` | cast | default |

### Employee

- **System of record:** `78b8b8fdb27f`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `78b8b8fdb27f` | `id` | none | skip |
| `name` | `78b8b8fdb27f` | `name` | none | skip |
| `role` | `78b8b8fdb27f` | `role` | none | skip |
| `trade` | `78b8b8fdb27f` | `trade` | none | skip |
| `base_rate` | `78b8b8fdb27f` | `base_rate` | cast | skip |
| `burden_rate` | `78b8b8fdb27f` | `burden_rate` | cast | skip |
| `bill_rate` | `78b8b8fdb27f` | `bill_rate` | cast | skip |
| `status` | `78b8b8fdb27f` | `status` | none | skip |
| `hire_date` | `78b8b8fdb27f` | `hire_date` | cast | skip |
| `termination_date` | `78b8b8fdb27f` | `termination_date` | cast | default |

### Estimate

- **System of record:** `ce1c4e604911`
- **Merge key:** `estimate_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `estimate_id` | `ce1c4e604911` | `estimate_id` | none | skip |
| `estimate_number` | `ce1c4e604911` | `estimate_number` | none | skip |
| `version` | `ce1c4e604911` | `version` | cast | skip |
| `customer_id` | `ce1c4e604911` | `customer_id` | none | skip |
| `archetype` | `ce1c4e604911` | `archetype` | none | skip |
| `status` | `ce1c4e604911` | `status` | none | skip |
| `scope_description` | `ce1c4e604911` | `scope_description` | none | skip |
| `exclusions` | `ce1c4e604911` | `exclusions` | none | skip |
| `assumptions` | `ce1c4e604911` | `assumptions` | none | skip |
| `total` | `ce1c4e604911` | `total` | cast | skip |
| `cost_estimate` | `ce1c4e604911` | `cost_estimate` | cast | skip |
| `markup_pct` | `ce1c4e604911` | `markup_pct` | cast | skip |
| `tax_amount` | `ce1c4e604911` | `tax_amount` | cast | default |
| `created_at` | `ce1c4e604911` | `created_at` | cast | skip |
| `sent_at` | `ce1c4e604911` | `sent_at` | cast | skip |
| `valid_until` | `ce1c4e604911` | `valid_until` | cast | skip |
| `accepted_at` | `ce1c4e604911` | `accepted_at` | cast | default |
| `project_id` | `ce1c4e604911` | `project_id` | none | default |

### EstimateLineItem

- **System of record:** `e03d6c5ed7d7`
- **Merge key:** `line_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `line_id` | `e03d6c5ed7d7` | `line_id` | none | skip |
| `estimate_id` | `e03d6c5ed7d7` | `estimate_id` | none | skip |
| `cost_code` | `e03d6c5ed7d7` | `cost_code` | none | skip |
| `description` | `e03d6c5ed7d7` | `description` | none | skip |
| `quantity` | `e03d6c5ed7d7` | `quantity` | cast | skip |
| `unit` | `e03d6c5ed7d7` | `unit` | none | skip |
| `unit_cost` | `e03d6c5ed7d7` | `unit_cost` | cast | skip |
| `unit_price` | `e03d6c5ed7d7` | `unit_price` | cast | skip |
| `line_total` | `e03d6c5ed7d7` | `line_total` | cast | skip |
| `category` | `e03d6c5ed7d7` | `category` | none | skip |

### Project

- **System of record:** `7b95d9ad0f5f`
- **Merge key:** `project_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `project_id` | `7b95d9ad0f5f` | `project_id` | none | skip |
| `estimate_id` | `7b95d9ad0f5f` | `estimate_id` | none | skip |
| `customer_id` | `7b95d9ad0f5f` | `customer_id` | none | skip |
| `name` | `7b95d9ad0f5f` | `name` | none | skip |
| `archetype` | `7b95d9ad0f5f` | `archetype` | none | skip |
| `type` | `7b95d9ad0f5f` | `type` | none | skip |
| `trade` | `7b95d9ad0f5f` | `trade` | none | skip |
| `status` | `7b95d9ad0f5f` | `status` | none | skip |
| `site_address` | `7b95d9ad0f5f` | `site_address` | none | skip |
| `start_date` | `7b95d9ad0f5f` | `start_date` | cast | skip |
| `end_date` | `7b95d9ad0f5f` | `end_date` | cast | skip |
| `actual_start` | `7b95d9ad0f5f` | `actual_start` | cast | skip |
| `actual_end` | `7b95d9ad0f5f` | `actual_end` | cast | skip |
| `contract_amount` | `7b95d9ad0f5f` | `contract_amount` | cast | skip |
| `contract_type` | `7b95d9ad0f5f` | `contract_type` | none | skip |
| `markup_pct` | `7b95d9ad0f5f` | `markup_pct` | cast | skip |
| `retention_pct` | `7b95d9ad0f5f` | `retention_pct` | cast | skip |
| `retention_released` | `7b95d9ad0f5f` | `retention_released` | cast | default |
| `permit_required` | `7b95d9ad0f5f` | `permit_required` | cast | default |
| `permit_number` | `7b95d9ad0f5f` | `permit_number` | none | default |

### Job

- **System of record:** `d8e86831c3bc`
- **Merge key:** `job_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `job_id` | `d8e86831c3bc` | `job_id` | none | skip |
| `project_id` | `d8e86831c3bc` | `project_id` | none | skip |
| `code` | `d8e86831c3bc` | `code` | none | skip |
| `name` | `d8e86831c3bc` | `name` | none | skip |
| `budgeted_labor_hours` | `d8e86831c3bc` | `budgeted_labor_hours` | cast | skip |
| `budgeted_labor_cost` | `d8e86831c3bc` | `budgeted_labor_cost` | cast | skip |
| `budgeted_material_cost` | `d8e86831c3bc` | `budgeted_material_cost` | cast | skip |
| `budgeted_sub_cost` | `d8e86831c3bc` | `budgeted_sub_cost` | cast | skip |
| `budgeted_equipment_cost` | `d8e86831c3bc` | `budgeted_equipment_cost` | cast | default |
| `budgeted_other_cost` | `d8e86831c3bc` | `budgeted_other_cost` | cast | default |
| `status` | `d8e86831c3bc` | `status` | none | skip |
| `sort_order` | `d8e86831c3bc` | `sort_order` | cast | skip |
| `sub_vendor_type` | `d8e86831c3bc` | `sub_vendor_type` | none | default |
| `equipment_needed` | `d8e86831c3bc` | `equipment_needed` | cast | default |
| `actual_start` | `d8e86831c3bc` | `actual_start` | cast | skip |
| `actual_end` | `d8e86831c3bc` | `actual_end` | cast | skip |

### TimeEntry

- **System of record:** `a1d7892ddd7d`
- **Merge key:** `entry_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `entry_id` | `a1d7892ddd7d` | `entry_id` | none | skip |
| `employee_id` | `a1d7892ddd7d` | `employee_id` | none | skip |
| `project_id` | `a1d7892ddd7d` | `project_id` | none | skip |
| `job_id` | `a1d7892ddd7d` | `job_id` | none | skip |
| `date` | `a1d7892ddd7d` | `date` | cast | skip |
| `hours_regular` | `a1d7892ddd7d` | `hours_regular` | cast | skip |
| `hours_overtime` | `a1d7892ddd7d` | `hours_overtime` | cast | default |
| `cost` | `a1d7892ddd7d` | `cost` | cast | skip |
| `notes` | `a1d7892ddd7d` | `notes` | none | skip |

### Bill

- **System of record:** `3ec971acc703`
- **Merge key:** `bill_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `bill_id` | `3ec971acc703` | `bill_id` | none | skip |
| `vendor_id` | `3ec971acc703` | `vendor_id` | none | skip |
| `project_id` | `3ec971acc703` | `project_id` | none | default |
| `job_id` | `3ec971acc703` | `job_id` | none | default |
| `vendor_invoice_number` | `3ec971acc703` | `vendor_invoice_number` | none | skip |
| `status` | `3ec971acc703` | `status` | none | skip |
| `received_date` | `3ec971acc703` | `received_date` | cast | skip |
| `due_date` | `3ec971acc703` | `due_date` | cast | skip |
| `total` | `3ec971acc703` | `total` | cast | skip |
| `paid_date` | `3ec971acc703` | `paid_date` | cast | skip |
| `payment_method` | `3ec971acc703` | `payment_method` | none | skip |
| `check_number` | `3ec971acc703` | `check_number` | cast | default |
| `category` | `3ec971acc703` | `category` | none | skip |

### BillLineItem

- **System of record:** `cc08c48ce725`
- **Merge key:** `line_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `line_id` | `cc08c48ce725` | `line_id` | none | skip |
| `bill_id` | `cc08c48ce725` | `bill_id` | none | skip |
| `project_id` | `cc08c48ce725` | `project_id` | none | default |
| `job_id` | `cc08c48ce725` | `job_id` | none | default |
| `description` | `cc08c48ce725` | `description` | none | skip |
| `quantity` | `cc08c48ce725` | `quantity` | cast | skip |
| `unit_cost` | `cc08c48ce725` | `unit_cost` | cast | skip |
| `line_total` | `cc08c48ce725` | `line_total` | cast | skip |
| `category` | `cc08c48ce725` | `category` | none | skip |

### Invoice

- **System of record:** `d03c595c4b33`
- **Merge key:** `invoice_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `invoice_id` | `d03c595c4b33` | `invoice_id` | none | skip |
| `invoice_number` | `d03c595c4b33` | `invoice_number` | none | skip |
| `project_id` | `d03c595c4b33` | `project_id` | none | skip |
| `customer_id` | `d03c595c4b33` | `customer_id` | none | skip |
| `type` | `d03c595c4b33` | `type` | none | skip |
| `status` | `d03c595c4b33` | `status` | none | skip |
| `issued_date` | `d03c595c4b33` | `issued_date` | cast | skip |
| `due_date` | `d03c595c4b33` | `due_date` | cast | skip |
| `subtotal` | `d03c595c4b33` | `subtotal` | cast | skip |
| `retention_held` | `d03c595c4b33` | `retention_held` | cast | skip |
| `tax` | `d03c595c4b33` | `tax` | cast | default |
| `total_due` | `d03c595c4b33` | `total_due` | cast | skip |

### Payment

- **System of record:** `491b7ff7ab76`
- **Merge key:** `payment_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `payment_id` | `491b7ff7ab76` | `payment_id` | none | skip |
| `invoice_id` | `491b7ff7ab76` | `invoice_id` | none | skip |
| `project_id` | `491b7ff7ab76` | `project_id` | none | skip |
| `customer_id` | `491b7ff7ab76` | `customer_id` | none | skip |
| `amount` | `491b7ff7ab76` | `amount` | cast | skip |
| `method` | `491b7ff7ab76` | `method` | none | skip |
| `reference` | `491b7ff7ab76` | `reference` | none | skip |
| `received_date` | `491b7ff7ab76` | `received_date` | cast | skip |
| `deposited_date` | `491b7ff7ab76` | `deposited_date` | cast | skip |

### NarrativeEvent

- **System of record:** `fadb29a0034e`
- **Merge key:** `event_id`
- **Conflict resolution:** not_applicable
- **Additional sources:** `d17411f8d40e`, `28104fac72b5`

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `event_id` | `fadb29a0034e` | `event_id` | none | skip |
| `event_type` | `fadb29a0034e` | `None` | calculate | skip |
| `date` | `fadb29a0034e` | `date` | cast | skip |
| `description` | `fadb29a0034e` | `description` | none | skip |
| `amount` | `fadb29a0034e` | `amount` | cast | default |
| `event_metadata` | `fadb29a0034e` | `None` | calculate | default |

## Relationship Mappings

| Relationship | Method | Source | From Field | To Field | Confidence |
|-------------|--------|--------|------------|----------|-----------|
| `customer_has_estimate` | fk_lookup | `ce1c4e604911` | `customer_id` | `estimate_id` | 1.0 |
| `customer_has_project` | fk_lookup | `7b95d9ad0f5f` | `customer_id` | `project_id` | 1.0 |
| `estimate_becomes_project` | fk_lookup | `7b95d9ad0f5f` | `estimate_id` | `project_id` | 1.0 |
| `estimate_has_line_item` | fk_lookup | `e03d6c5ed7d7` | `estimate_id` | `line_id` | 1.0 |
| `project_has_job` | fk_lookup | `d8e86831c3bc` | `project_id` | `job_id` | 1.0 |
| `project_has_invoice` | fk_lookup | `d03c595c4b33` | `project_id` | `invoice_id` | 1.0 |
| `project_has_bill` | fk_lookup | `3ec971acc703` | `project_id` | `bill_id` | 1.0 |
| `job_has_time_entry` | fk_lookup | `a1d7892ddd7d` | `job_id` | `entry_id` | 0.792 |
| `job_has_bill` | fk_lookup | `3ec971acc703` | `job_id` | `bill_id` | 0.829 |
| `employee_logs_time` | fk_lookup | `a1d7892ddd7d` | `employee_id` | `entry_id` | 0.86 |
| `vendor_has_bill` | fk_lookup | `3ec971acc703` | `vendor_id` | `bill_id` | 0.93 |
| `invoice_has_payment` | fk_lookup | `491b7ff7ab76` | `invoice_id` | `payment_id` | 1.0 |
| `company_employs` | fk_lookup | `381f49880b21` | `owner_employee_id` | `name` | 0.44 |
| `estimate_line_item_maps_to_job` | fk_lookup | `e03d6c5ed7d7` | `cost_code` | `job_id` | 1.0 |

## Statistical Computations

### project_gross_margin

**Target:** `Project.gross_margin`
**Formula:** `(contract_amount - (sum(bill.total where project_id matches) + sum(time_entry.cost where project_id matches))) / contract_amount`
**Output type:** float

**Inputs:**
- `7b95d9ad0f5f.contract_amount` → None
- `3ec971acc703.total` → sum
- `a1d7892ddd7d.cost` → sum

### project_total_costs

**Target:** `Project.total_costs`
**Formula:** `sum(bill.total where project_id matches) + sum(time_entry.cost where project_id matches)`
**Output type:** float

**Inputs:**
- `3ec971acc703.total` → sum
- `a1d7892ddd7d.cost` → sum

### employee_utilization

**Target:** `Employee.utilization_rate`
**Formula:** `(sum(hours_regular) + sum(hours_overtime)) / (available_working_days * 8)`
**Output type:** float

**Inputs:**
- `a1d7892ddd7d.hours_regular` → sum (window: trailing_12m)
- `a1d7892ddd7d.hours_overtime` → sum (window: trailing_12m)

### customer_lifetime_value

**Target:** `Customer.lifetime_value`
**Formula:** `sum(project.contract_amount where customer_id matches)`
**Output type:** float

**Inputs:**
- `7b95d9ad0f5f.contract_amount` → sum

### vendor_spend

**Target:** `Vendor.total_spend`
**Formula:** `sum(bill.total where vendor_id matches and received_date within trailing 12 months)`
**Output type:** float

**Inputs:**
- `3ec971acc703.total` → sum (window: trailing_12m)

### project_cost_variance

**Target:** `Project.cost_variance`
**Formula:** `((sum(bill.total) + sum(time_entry.cost)) - estimate.cost_estimate) / estimate.cost_estimate`
**Output type:** float

**Inputs:**
- `3ec971acc703.total` → sum
- `a1d7892ddd7d.cost` → sum
- `ce1c4e604911.cost_estimate` → None

## Source Utilization

**Consumed:** 16 sources | **Excluded:** 2 sources

### Excluded Sources

- `data_json`: Alternate format of same data. CSV files are the primary source.
- `builder_db`: Alternate format of same data. CSV files are the primary source.
