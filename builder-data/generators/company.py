"""Load company config and seed the registry with stable master data."""
from datetime import date, datetime

import yaml

from .base import Registry


def load_config(config_dir: str) -> dict:
    configs = {}
    for name in ("company", "archetypes", "events"):
        with open(f"{config_dir}/{name}.yaml") as f:
            configs[name] = yaml.safe_load(f)
    return configs


def seed_master_data(cfg: dict, registry: Registry) -> None:
    """Load customers, vendors, and initial employee roster into the registry."""
    company_cfg = cfg["company"]
    archetypes_cfg = cfg["archetypes"]

    # ── Company ─────────────────────────────────────────────────────────────
    registry.add("company", {
        "name": company_cfg["company"]["name"],
        "trade": company_cfg["company"]["trade"],
        "region": company_cfg["company"]["region"],
        "owner_name": company_cfg["company"]["owner_name"],
        "owner_employee_id": company_cfg["company"]["owner_employee_id"],
        "address": company_cfg["company"]["address"],
        "phone": company_cfg["company"]["phone"],
        "email": company_cfg["company"]["email"],
        "license_number": company_cfg["company"]["license_number"],
    })

    # ── Vendors ──────────────────────────────────────────────────────────────
    for v in company_cfg["vendors"]:
        registry.add("vendor", dict(v))

    # ── Customers ────────────────────────────────────────────────────────────
    customers_cfg = cfg.get("customers", archetypes_cfg.get("customers", {}))
    for ctype in ("residential", "commercial"):
        for c in customers_cfg.get(ctype, []):
            record = dict(c)
            record["type"] = ctype
            record.setdefault("tax_exempt", False)
            record.setdefault("credit_limit", 0)
            record.setdefault("status", "active")
            record["created_at"] = "2024-01-01"
            registry.add("customer", record)

    # ── Initial Employees (snapshot at timeline start) ───────────────────────
    _apply_crew_snapshot(company_cfg, date(2024, 1, 1), registry)


def _apply_crew_snapshot(company_cfg: dict, as_of: date, registry: Registry) -> None:
    """Apply all crew timeline events up to as_of and build the active roster."""
    timeline = company_cfg.get("crew_timeline", [])
    for event in timeline:
        event_date = date.fromisoformat(event["date"])
        if event_date > as_of:
            break

        if "employees" in event:
            # Full roster snapshot
            for emp in event["employees"]:
                existing = registry.by_id("employee", "id", emp["id"])
                if not existing:
                    record = dict(emp)
                    record["status"] = "active"
                    record["hire_date"] = event["date"]
                    record["termination_date"] = None
                    registry.add("employee", record)
        if "add" in event:
            for emp in event["add"]:
                existing = registry.by_id("employee", "id", emp["id"])
                if not existing:
                    record = dict(emp)
                    record["status"] = "active"
                    record["hire_date"] = event["date"]
                    record["termination_date"] = None
                    registry.add("employee", record)
        if "promote" in event:
            p = event["promote"]
            emp = registry.by_id("employee", "id", p["id"])
            if emp:
                emp["role"] = p["new_role"]
                emp["base_rate"] = p["new_base_rate"]
                emp["burden_rate"] = p["new_burden_rate"]
                emp["bill_rate"] = p["new_bill_rate"]
        if "terminate" in event:
            t = event["terminate"]
            emp = registry.by_id("employee", "id", t["id"])
            if emp:
                emp["status"] = "terminated"
                emp["termination_date"] = event["date"]


def get_active_crew(registry: Registry, as_of: date, company_cfg: dict) -> list[dict]:
    """Return employees who were active on a given date."""
    # Re-apply timeline up to as_of to get correct state
    # For simplicity, return all employees whose hire_date <= as_of and
    # termination_date is None or > as_of
    result = []
    for emp in registry.all("employee"):
        hire = date.fromisoformat(emp["hire_date"])
        term_raw = emp.get("termination_date")
        term = date.fromisoformat(term_raw) if term_raw else None
        if hire <= as_of and (term is None or term > as_of):
            result.append(emp)
    return result
