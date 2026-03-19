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

- **System of record:** `company`
- **Merge key:** `name`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `name` | `company` | `name` | none | skip |
| `trade` | `company` | `trade` | none | skip |
| `region` | `company` | `region` | none | skip |
| `owner_name` | `company` | `owner_name` | none | skip |
| `owner_employee_id` | `company` | `owner_employee_id` | none | skip |
| `address` | `company` | `address` | none | skip |
| `phone` | `company` | `phone` | none | skip |
| `email` | `company` | `email` | none | skip |
| `license_number` | `company` | `license_number` | none | skip |

### Customer

- **System of record:** `customer`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `customer` | `id` | none | skip |
| `name` | `customer` | `name` | none | skip |
| `email` | `customer` | `email` | none | skip |
| `phone` | `customer` | `phone` | none | skip |
| `address` | `customer` | `address` | none | skip |
| `payment_terms` | `customer` | `payment_terms` | normalize | skip |
| `source` | `customer` | `source` | normalize | skip |
| `type` | `customer` | `type` | normalize | skip |
| `tax_exempt` | `customer` | `tax_exempt` | cast | default |
| `credit_limit` | `customer` | `credit_limit` | cast | default |
| `status` | `customer` | `status` | none | skip |
| `created_at` | `customer` | `created_at` | cast | skip |
| `notes` | `customer` | `notes` | none | default |

### Vendor

- **System of record:** `vendor`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `vendor` | `id` | none | skip |
| `name` | `vendor` | `name` | none | skip |
| `type` | `vendor` | `type` | normalize | skip |
| `trade` | `vendor` | `trade` | none | default |
| `contact` | `vendor` | `contact` | none | default |
| `phone` | `vendor` | `phone` | none | default |
| `email` | `vendor` | `email` | none | default |
| `payment_terms` | `vendor` | `payment_terms` | normalize | skip |
| `tax_id` | `vendor` | `tax_id` | none | default |
| `w9_on_file` | `vendor` | `w9_on_file` | cast | default |
| `insurance_expiry` | `vendor` | `insurance_expiry` | cast | default |
| `rating` | `vendor` | `rating` | cast | default |
| `credit_limit` | `vendor` | `credit_limit` | cast | default |
| `account_opened` | `vendor` | `account_opened` | cast | default |

### Employee

- **System of record:** `employee`
- **Merge key:** `id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `id` | `employee` | `id` | none | skip |
| `name` | `employee` | `name` | none | skip |
| `role` | `employee` | `role` | none | skip |
| `trade` | `employee` | `trade` | none | skip |
| `base_rate` | `employee` | `base_rate` | cast | skip |
| `burden_rate` | `employee` | `burden_rate` | cast | skip |
| `bill_rate` | `employee` | `bill_rate` | cast | skip |
| `status` | `employee` | `status` | none | skip |
| `hire_date` | `employee` | `hire_date` | cast | skip |
| `termination_date` | `employee` | `termination_date` | cast | default |

### Estimate

- **System of record:** `estimate`
- **Merge key:** `estimate_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `estimate_id` | `estimate` | `estimate_id` | none | skip |
| `estimate_number` | `estimate` | `estimate_number` | none | skip |
| `version` | `estimate` | `version` | cast | skip |
| `customer_id` | `estimate` | `customer_id` | none | skip |
| `archetype` | `estimate` | `archetype` | none | skip |
| `status` | `estimate` | `status` | none | skip |
| `scope_description` | `estimate` | `scope_description` | none | skip |
| `exclusions` | `estimate` | `exclusions` | none | skip |
| `assumptions` | `estimate` | `assumptions` | none | skip |
| `total` | `estimate` | `total` | cast | skip |
| `cost_estimate` | `estimate` | `cost_estimate` | cast | skip |
| `markup_pct` | `estimate` | `markup_pct` | cast | skip |
| `tax_amount` | `estimate` | `tax_amount` | cast | default |
| `created_at` | `estimate` | `created_at` | cast | skip |
| `sent_at` | `estimate` | `sent_at` | cast | skip |
| `valid_until` | `estimate` | `valid_until` | cast | skip |
| `accepted_at` | `estimate` | `accepted_at` | cast | default |
| `project_id` | `estimate` | `project_id` | none | default |

### EstimateLineItem

- **System of record:** `estimate_line_item`
- **Merge key:** `line_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `line_id` | `estimate_line_item` | `line_id` | none | skip |
| `estimate_id` | `estimate_line_item` | `estimate_id` | none | skip |
| `cost_code` | `estimate_line_item` | `cost_code` | none | skip |
| `description` | `estimate_line_item` | `description` | none | skip |
| `quantity` | `estimate_line_item` | `quantity` | cast | skip |
| `unit` | `estimate_line_item` | `unit` | none | skip |
| `unit_cost` | `estimate_line_item` | `unit_cost` | cast | skip |
| `unit_price` | `estimate_line_item` | `unit_price` | cast | skip |
| `line_total` | `estimate_line_item` | `line_total` | cast | skip |
| `category` | `estimate_line_item` | `category` | none | skip |

### Project

- **System of record:** `project`
- **Merge key:** `project_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `project_id` | `project` | `project_id` | none | skip |
| `estimate_id` | `project` | `estimate_id` | none | skip |
| `customer_id` | `project` | `customer_id` | none | skip |
| `name` | `project` | `name` | none | skip |
| `archetype` | `project` | `archetype` | none | skip |
| `type` | `project` | `type` | none | skip |
| `trade` | `project` | `trade` | none | skip |
| `status` | `project` | `status` | none | skip |
| `site_address` | `project` | `site_address` | none | skip |
| `start_date` | `project` | `start_date` | cast | skip |
| `end_date` | `project` | `end_date` | cast | skip |
| `actual_start` | `project` | `actual_start` | cast | skip |
| `actual_end` | `project` | `actual_end` | cast | skip |
| `contract_amount` | `project` | `contract_amount` | cast | skip |
| `contract_type` | `project` | `contract_type` | none | skip |
| `markup_pct` | `project` | `markup_pct` | cast | skip |
| `retention_pct` | `project` | `retention_pct` | cast | skip |
| `retention_released` | `project` | `retention_released` | cast | default |
| `permit_required` | `project` | `permit_required` | cast | default |
| `permit_number` | `project` | `permit_number` | none | default |

### Job

- **System of record:** `job`
- **Merge key:** `job_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `job_id` | `job` | `job_id` | none | skip |
| `project_id` | `job` | `project_id` | none | skip |
| `code` | `job` | `code` | none | skip |
| `name` | `job` | `name` | none | skip |
| `budgeted_labor_hours` | `job` | `budgeted_labor_hours` | cast | skip |
| `budgeted_labor_cost` | `job` | `budgeted_labor_cost` | cast | skip |
| `budgeted_material_cost` | `job` | `budgeted_material_cost` | cast | skip |
| `budgeted_sub_cost` | `job` | `budgeted_sub_cost` | cast | skip |
| `budgeted_equipment_cost` | `job` | `budgeted_equipment_cost` | cast | default |
| `budgeted_other_cost` | `job` | `budgeted_other_cost` | cast | default |
| `status` | `job` | `status` | none | skip |
| `sort_order` | `job` | `sort_order` | cast | skip |
| `sub_vendor_type` | `job` | `sub_vendor_type` | none | default |
| `equipment_needed` | `job` | `equipment_needed` | cast | default |
| `actual_start` | `job` | `actual_start` | cast | skip |
| `actual_end` | `job` | `actual_end` | cast | skip |

### TimeEntry

- **System of record:** `time_entry`
- **Merge key:** `entry_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `entry_id` | `time_entry` | `entry_id` | none | skip |
| `employee_id` | `time_entry` | `employee_id` | none | skip |
| `project_id` | `time_entry` | `project_id` | none | skip |
| `job_id` | `time_entry` | `job_id` | none | skip |
| `date` | `time_entry` | `date` | cast | skip |
| `hours_regular` | `time_entry` | `hours_regular` | cast | skip |
| `hours_overtime` | `time_entry` | `hours_overtime` | cast | default |
| `cost` | `time_entry` | `cost` | cast | skip |
| `notes` | `time_entry` | `notes` | none | skip |

### Bill

- **System of record:** `bill`
- **Merge key:** `bill_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `bill_id` | `bill` | `bill_id` | none | skip |
| `vendor_id` | `bill` | `vendor_id` | none | skip |
| `project_id` | `bill` | `project_id` | none | default |
| `job_id` | `bill` | `job_id` | none | default |
| `vendor_invoice_number` | `bill` | `vendor_invoice_number` | none | skip |
| `status` | `bill` | `status` | none | skip |
| `received_date` | `bill` | `received_date` | cast | skip |
| `due_date` | `bill` | `due_date` | cast | skip |
| `total` | `bill` | `total` | cast | skip |
| `paid_date` | `bill` | `paid_date` | cast | skip |
| `payment_method` | `bill` | `payment_method` | none | skip |
| `check_number` | `bill` | `check_number` | cast | default |
| `category` | `bill` | `category` | none | skip |

### BillLineItem

- **System of record:** `bill_line_item`
- **Merge key:** `line_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `line_id` | `bill_line_item` | `line_id` | none | skip |
| `bill_id` | `bill_line_item` | `bill_id` | none | skip |
| `project_id` | `bill_line_item` | `project_id` | none | default |
| `job_id` | `bill_line_item` | `job_id` | none | default |
| `description` | `bill_line_item` | `description` | none | skip |
| `quantity` | `bill_line_item` | `quantity` | cast | skip |
| `unit_cost` | `bill_line_item` | `unit_cost` | cast | skip |
| `line_total` | `bill_line_item` | `line_total` | cast | skip |
| `category` | `bill_line_item` | `category` | none | skip |

### Invoice

- **System of record:** `invoice`
- **Merge key:** `invoice_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `invoice_id` | `invoice` | `invoice_id` | none | skip |
| `invoice_number` | `invoice` | `invoice_number` | none | skip |
| `project_id` | `invoice` | `project_id` | none | skip |
| `customer_id` | `invoice` | `customer_id` | none | skip |
| `type` | `invoice` | `type` | none | skip |
| `status` | `invoice` | `status` | none | skip |
| `issued_date` | `invoice` | `issued_date` | cast | skip |
| `due_date` | `invoice` | `due_date` | cast | skip |
| `subtotal` | `invoice` | `subtotal` | cast | skip |
| `retention_held` | `invoice` | `retention_held` | cast | skip |
| `tax` | `invoice` | `tax` | cast | default |
| `total_due` | `invoice` | `total_due` | cast | skip |

### Payment

- **System of record:** `payment`
- **Merge key:** `payment_id`
- **Conflict resolution:** not_applicable

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `payment_id` | `payment` | `payment_id` | none | skip |
| `invoice_id` | `payment` | `invoice_id` | none | skip |
| `project_id` | `payment` | `project_id` | none | skip |
| `customer_id` | `payment` | `customer_id` | none | skip |
| `amount` | `payment` | `amount` | cast | skip |
| `method` | `payment` | `method` | none | skip |
| `reference` | `payment` | `reference` | none | skip |
| `received_date` | `payment` | `received_date` | cast | skip |
| `deposited_date` | `payment` | `deposited_date` | cast | skip |

### NarrativeEvent

- **System of record:** `loc_event`
- **Merge key:** `event_id`
- **Conflict resolution:** not_applicable
- **Additional sources:** `overtime_event`, `pricing_change`

| Target Property | Source | Source Field | Transform | Null Handling |
|----------------|--------|-------------|-----------|---------------|
| `event_id` | `loc_event` | `event_id` | none | skip |
| `event_type` | `loc_event` | `None` | calculate | skip |
| `date` | `loc_event` | `date` | cast | skip |
| `description` | `loc_event` | `description` | none | skip |
| `amount` | `loc_event` | `amount` | cast | default |
| `event_metadata` | `loc_event` | `None` | calculate | default |

## Relationship Mappings

| Relationship | Method | Source | From Field | To Field | Confidence |
|-------------|--------|--------|------------|----------|-----------|
| `customer_has_estimate` | fk_lookup | `estimate` | `customer_id` | `estimate_id` | 1.0 |
| `customer_has_project` | fk_lookup | `project` | `customer_id` | `project_id` | 1.0 |
| `estimate_becomes_project` | fk_lookup | `project` | `estimate_id` | `project_id` | 1.0 |
| `estimate_has_line_item` | fk_lookup | `estimate_line_item` | `estimate_id` | `line_id` | 1.0 |
| `project_has_job` | fk_lookup | `job` | `project_id` | `job_id` | 1.0 |
| `project_has_invoice` | fk_lookup | `invoice` | `project_id` | `invoice_id` | 1.0 |
| `project_has_bill` | fk_lookup | `bill` | `project_id` | `bill_id` | 1.0 |
| `job_has_time_entry` | fk_lookup | `time_entry` | `job_id` | `entry_id` | 0.792 |
| `job_has_bill` | fk_lookup | `bill` | `job_id` | `bill_id` | 0.829 |
| `employee_logs_time` | fk_lookup | `time_entry` | `employee_id` | `entry_id` | 0.86 |
| `vendor_has_bill` | fk_lookup | `bill` | `vendor_id` | `bill_id` | 0.93 |
| `invoice_has_payment` | fk_lookup | `payment` | `invoice_id` | `payment_id` | 1.0 |
| `company_employs` | fk_lookup | `company` | `owner_employee_id` | `name` | 0.44 |
| `estimate_line_item_maps_to_job` | fk_lookup | `estimate_line_item` | `cost_code` | `job_id` | 1.0 |

## Statistical Computations

### project_gross_margin

**Target:** `Project.gross_margin`
**Formula:** `(contract_amount - (sum(bill.total where project_id matches) + sum(time_entry.cost where project_id matches))) / contract_amount`
**Output type:** float

**Inputs:**
- `project.contract_amount` → None
- `bill.total` → sum
- `time_entry.cost` → sum

### project_total_costs

**Target:** `Project.total_costs`
**Formula:** `sum(bill.total where project_id matches) + sum(time_entry.cost where project_id matches)`
**Output type:** float

**Inputs:**
- `bill.total` → sum
- `time_entry.cost` → sum

### employee_utilization

**Target:** `Employee.utilization_rate`
**Formula:** `(sum(hours_regular) + sum(hours_overtime)) / (available_working_days * 8)`
**Output type:** float

**Inputs:**
- `time_entry.hours_regular` → sum (window: trailing_12m)
- `time_entry.hours_overtime` → sum (window: trailing_12m)

### customer_lifetime_value

**Target:** `Customer.lifetime_value`
**Formula:** `sum(project.contract_amount where customer_id matches)`
**Output type:** float

**Inputs:**
- `project.contract_amount` → sum

### vendor_spend

**Target:** `Vendor.total_spend`
**Formula:** `sum(bill.total where vendor_id matches and received_date within trailing 12 months)`
**Output type:** float

**Inputs:**
- `bill.total` → sum (window: trailing_12m)

### project_cost_variance

**Target:** `Project.cost_variance`
**Formula:** `((sum(bill.total) + sum(time_entry.cost)) - estimate.cost_estimate) / estimate.cost_estimate`
**Output type:** float

**Inputs:**
- `bill.total` → sum
- `time_entry.cost` → sum
- `estimate.cost_estimate` → None

## Source Utilization

**Consumed:** 16 sources | **Excluded:** 2 sources

### Excluded Sources

- `data_json`: Alternate format of same data. CSV files are the primary source.
- `builder_db`: Alternate format of same data. CSV files are the primary source.
