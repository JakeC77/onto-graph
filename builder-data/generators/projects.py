"""Generate the project pipeline: estimates, projects, jobs, change orders."""
import random
from datetime import date, timedelta
from typing import Optional

from .base import Registry, uid, rand_between, rand_int, seasonal_weight, apply_variance, round_to_cents


# Map archetype sub_vendor_type strings to vendor types in registry
VENDOR_TYPE_MAP = {
    "plumbing": "subcontractor",
    "electrical": "subcontractor",
    "hvac": "subcontractor",
    "tile": "subcontractor",
    "countertops": "subcontractor",
}

# Archetype trade to narrow vendor lookup
VENDOR_TRADE_MAP = {
    "plumbing": "plumbing",
    "electrical": "electrical",
    "hvac": "hvac",
    "tile": "tile",
    "countertops": "countertops",
}


def _pick_vendor(registry: Registry, sub_vendor_type: str) -> Optional[dict]:
    trade = VENDOR_TRADE_MAP.get(sub_vendor_type)
    if not trade:
        return None
    candidates = [v for v in registry.all("vendor")
                  if v.get("type") == "subcontractor" and v.get("trade") == trade]
    return random.choice(candidates) if candidates else None


def _pick_customer(registry: Registry, customer_type) -> Optional[dict]:
    if isinstance(customer_type, list):
        ctype = random.choice(customer_type)
    else:
        ctype = customer_type
    candidates = registry.filter("customer", type=ctype)
    return random.choice(candidates) if candidates else None


def _estimate_number(registry: Registry) -> str:
    count = len(registry.all("estimate")) + 1
    return f"EST-{count:04d}"


def _invoice_number(registry: Registry) -> str:
    count = len(registry.all("invoice")) + 1
    return f"INV-{count:04d}"


def generate_project_pipeline(
    cfg: dict,
    registry: Registry,
    start_date: date,
    end_date: date,
    rng: random.Random,
    narrative_tags: dict,  # tag -> event config
) -> None:
    """
    Generate all estimates (won + lost) for the simulation period.
    Won estimates become Projects with Jobs.
    """
    archetypes = cfg["archetypes"]
    company = cfg["company"]
    win_rates = company.get("win_rate_by_type", company.get("financials", {}).get("win_rate_by_type", {}))

    # Build a weighted pool of archetypes to sample from
    archetype_keys = [k for k in archetypes if k != "customers"]
    # Approximate frequency weights by typical job mix for a GC
    archetype_weights = {
        "kitchen_remodel": 6,
        "bathroom_remodel": 8,
        "deck_addition": 5,
        "room_addition": 3,
        "new_construction": 1,
        "repair_service": 12,
        "tenant_improvement": 2,
    }
    weights = [archetype_weights.get(k, 3) for k in archetype_keys]

    current = start_date
    while current < end_date:
        # How many estimates go out this month?
        # Peak season (May-Aug) generates more; winter fewer
        month = current.month
        base_estimates_per_month = 4
        sw = seasonal_weight(month, [0.6, 0.7, 0.9, 1.1, 1.3, 1.4, 1.4, 1.3, 1.2, 1.1, 0.8, 0.6])
        n_estimates = max(1, round(base_estimates_per_month * sw + rng.gauss(0, 0.5)))

        for _ in range(n_estimates):
            arch_key = rng.choices(archetype_keys, weights=weights, k=1)[0]
            arch = archetypes[arch_key]

            # Estimate date within this month
            month_end = date(current.year, current.month,
                             28 if current.month in (2,) else 30)
            est_date = current + timedelta(days=rng.randint(0, min(28, (month_end - current).days)))

            # Customer
            customer = _pick_customer(registry, arch.get("customer_type", "residential"))
            if not customer:
                continue

            # Contract value
            lo, hi = arch["contract_value"]
            sw_proj = seasonal_weight(est_date.month, arch["seasonal_weight"])
            mid = (lo + hi) / 2
            value = clamp_val(apply_variance(mid * sw_proj, 0.25), lo * 0.7, hi * 1.3)
            value = round_to_cents(value)

            # Margin
            margin_lo, margin_hi = arch["target_margin"]
            target_margin = rng.uniform(margin_lo, margin_hi)
            cost_estimate = round_to_cents(value * (1 - target_margin))

            est_id = uid("EST-")
            est_num = _estimate_number(registry)

            est = registry.add("estimate", {
                "estimate_id": est_id,
                "estimate_number": est_num,
                "version": 1,
                "customer_id": customer["id"],
                "archetype": arch_key,
                "status": "draft",
                "scope_description": _scope_description(arch_key, value),
                "exclusions": _exclusions(arch_key),
                "assumptions": _assumptions(arch_key),
                "total": value,
                "cost_estimate": cost_estimate,
                "markup_pct": round((value - cost_estimate) / cost_estimate, 4) if cost_estimate > 0 else 0,
                "tax_amount": 0.0,
                "created_at": est_date.isoformat(),
                "sent_at": (est_date + timedelta(days=rng.randint(1, 4))).isoformat(),
                "valid_until": (est_date + timedelta(days=30)).isoformat(),
                "accepted_at": None,
                "project_id": None,
                "narrative_tag": None,
            })

            # Build line items
            _generate_estimate_line_items(est, arch, registry, rng)

            # Win/loss
            win_rate = win_rates.get(arch["type"], 0.55)
            won = rng.random() < win_rate
            sent_date = date.fromisoformat(est["sent_at"])
            decision_date = sent_date + timedelta(days=rng.randint(3, 21))

            if decision_date > end_date:
                est["status"] = "sent"
                continue

            if won:
                est["status"] = "accepted"
                est["accepted_at"] = decision_date.isoformat()
                # Generate project from estimate
                project = _create_project(est, arch, registry, rng, decision_date, narrative_tags)
                est["project_id"] = project["project_id"]
            else:
                est["status"] = rng.choices(["declined", "expired"], weights=[0.6, 0.4])[0]

        # Advance to next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def clamp_val(v, lo, hi):
    return max(lo, min(hi, v))


def _create_project(est: dict, arch: dict, registry: Registry, rng: random.Random,
                    award_date: date, narrative_tags: dict) -> dict:
    proj_id = uid("PROJ-")
    duration_weeks = rng.uniform(*arch["duration_weeks"])
    start = award_date + timedelta(days=rng.randint(7, 28))
    end = start + timedelta(weeks=duration_weeks)
    permit_required = rng.random() < arch.get("permit_required_pct", 0.5)

    customer = registry.by_id("customer", "id", est["customer_id"])
    project_name = _project_name(customer, arch["label"])

    # Check if this matches a narrative tag
    tag = None
    for t_key in narrative_tags:
        if t_key in project_name.lower().replace(" ", "_"):
            tag = t_key

    retention_pct = arch.get("retention_pct", 0.05)

    project = registry.add("project", {
        "project_id": proj_id,
        "estimate_id": est["estimate_id"],
        "customer_id": est["customer_id"],
        "name": project_name,
        "archetype": est["archetype"],
        "type": arch["type"],
        "trade": arch.get("trade", "general"),
        "status": "awarded",
        "site_address": customer.get("address", ""),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "actual_start": None,
        "actual_end": None,
        "contract_amount": est["total"],
        "contract_type": "fixed_price",
        "markup_pct": est["markup_pct"],
        "retention_pct": retention_pct,
        "retention_released": False,
        "permit_required": permit_required,
        "permit_number": f"BLDG-{rng.randint(10000,99999)}" if permit_required else None,
        "narrative_tag": tag,
        "notes": "",
    })

    # Generate jobs (phases) from archetype
    _create_jobs(project, arch, est, registry)

    return project


def _create_jobs(project: dict, arch: dict, est: dict, registry: Registry) -> None:
    total_cost = est["cost_estimate"]
    for i, phase in enumerate(arch.get("phases", [])):
        labor_cost = round_to_cents(total_cost * phase["labor_pct"])
        material_cost = round_to_cents(total_cost * phase["material_pct"])
        sub_cost = round_to_cents(total_cost * phase["sub_pct"])

        # Budget labor hours from cost
        # Use average burden rate ~$35/hr
        avg_burden = 35.0
        budgeted_hours = round(labor_cost / avg_burden, 1) if labor_cost > 0 else 0.0

        job = registry.add("job", {
            "job_id": uid("JOB-"),
            "project_id": project["project_id"],
            "code": phase["code"],
            "name": phase["name"],
            "budgeted_labor_hours": budgeted_hours,
            "budgeted_labor_cost": labor_cost,
            "budgeted_material_cost": material_cost,
            "budgeted_sub_cost": sub_cost,
            "budgeted_equipment_cost": 0.0,
            "budgeted_other_cost": 0.0,
            "status": "not_started",
            "sort_order": i,
            "sub_vendor_type": phase.get("sub_vendor_type"),
            "equipment_needed": phase.get("equipment_needed", False),
        })


def _generate_estimate_line_items(est: dict, arch: dict, registry: Registry,
                                   rng: random.Random) -> None:
    total = est["total"]
    total_cost = est["cost_estimate"]

    for phase in arch.get("phases", []):
        labor_price = total * phase["labor_pct"]
        material_price = total * phase["material_pct"]
        sub_price = total * phase["sub_pct"]

        labor_cost = total_cost * phase["labor_pct"]
        material_cost = total_cost * phase["material_pct"]
        sub_cost = total_cost * phase["sub_pct"]

        if labor_price > 0:
            registry.add("estimate_line_item", {
                "line_id": uid("ELI-"),
                "estimate_id": est["estimate_id"],
                "cost_code": phase["code"],
                "description": f"{phase['name']} — Labor",
                "quantity": 1,
                "unit": "ls",
                "unit_cost": round_to_cents(labor_cost),
                "unit_price": round_to_cents(labor_price),
                "line_total": round_to_cents(labor_price),
                "category": "labor",
            })

        if material_price > 0:
            registry.add("estimate_line_item", {
                "line_id": uid("ELI-"),
                "estimate_id": est["estimate_id"],
                "cost_code": phase["code"],
                "description": f"{phase['name']} — Materials",
                "quantity": 1,
                "unit": "ls",
                "unit_cost": round_to_cents(material_cost),
                "unit_price": round_to_cents(material_price),
                "line_total": round_to_cents(material_price),
                "category": "material",
            })

        if sub_price > 0:
            registry.add("estimate_line_item", {
                "line_id": uid("ELI-"),
                "estimate_id": est["estimate_id"],
                "cost_code": phase["code"],
                "description": f"{phase['name']} — Subcontractor",
                "quantity": 1,
                "unit": "ls",
                "unit_cost": round_to_cents(sub_cost),
                "unit_price": round_to_cents(sub_price),
                "line_total": round_to_cents(sub_price),
                "category": "subcontractor",
            })


def _project_name(customer: dict, arch_label: str) -> str:
    if not customer:
        return f"Unknown — {arch_label}"
    name = customer["name"]
    # Extract last name(s)
    parts = name.replace("&", "and").split()
    # Find last name (last word, or second-to-last before "and second_last")
    last = parts[-1] if parts else name
    return f"{last} — {arch_label}"


def _scope_description(arch_key: str, value: float) -> str:
    descriptions = {
        "kitchen_remodel": "Complete kitchen renovation including demo, rough work, cabinets, countertops, tile backsplash, fixtures, and paint.",
        "bathroom_remodel": "Full bathroom renovation including demo, plumbing rough-in, tile shower/floor, vanity, fixtures, and paint.",
        "deck_addition": "New pressure-treated deck with composite decking, stairs, railings, and post footings.",
        "room_addition": "New room addition including foundation, framing, roofing, MEP rough-ins, insulation, drywall, trim, and flooring.",
        "new_construction": "New single-family home construction per plans and specifications.",
        "repair_service": "Repair and service work per scope discussed on site.",
        "tenant_improvement": "Commercial tenant improvement per plans including demo, framing, MEP, finishes.",
    }
    return descriptions.get(arch_key, "Work per scope discussed.")


def _exclusions(arch_key: str) -> str:
    exclusions = {
        "kitchen_remodel": "Appliances (unless noted), structural modifications, permits beyond standard building permit.",
        "bathroom_remodel": "Heated floor systems, steam generators, custom glass enclosures.",
        "deck_addition": "Landscaping, underground utilities, HOA approvals.",
        "room_addition": "Furniture, window treatments, landscaping restoration.",
        "new_construction": "Lot/land, financing, furniture, landscaping beyond final grade.",
        "repair_service": "Unrelated work discovered during service call.",
        "tenant_improvement": "FF&E, signage, low-voltage data cabling (unless noted), security systems.",
    }
    return exclusions.get(arch_key, "Work not explicitly listed in scope.")


def _assumptions(arch_key: str) -> str:
    assumptions = {
        "kitchen_remodel": "Existing plumbing and electrical locations remain. No asbestos or lead paint. Customer selects materials within allowances.",
        "bathroom_remodel": "Existing drain locations remain. No structural modifications to wet wall.",
        "deck_addition": "Site is accessible by equipment. Soil bearing capacity adequate for post footings.",
        "room_addition": "Permit approval within 4 weeks of submission. No unforeseen underground obstructions.",
        "new_construction": "Plans are fully permitted. Utility connections available at property line.",
        "repair_service": "Materials available locally. No concealed damage beyond visible scope.",
        "tenant_improvement": "Base building in good condition. Existing HVAC capacity adequate for new layout.",
    }
    return assumptions.get(arch_key, "Site conditions as represented.")
