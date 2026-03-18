"""Generate invoices, payments, overhead bills."""
import random
from datetime import date, timedelta
from typing import Optional

from .base import Registry, uid, round_to_cents


def generate_invoices(cfg: dict, registry: Registry, rng: random.Random,
                       events_by_tag: dict) -> None:
    """
    For each completed project, generate progress invoices and a final invoice.
    Apply payment lag from customer payment terms + narrative events.
    """
    company_cfg = cfg["company"]
    default_retention = company_cfg["financials"].get("default_retention_pct", 0.05)

    for project in registry.all("project"):
        if project["status"] not in ("complete", "in_progress"):
            continue

        contract = project["contract_amount"]
        retention_pct = project.get("retention_pct", default_retention)
        archetype = project.get("archetype", "")
        project_start = date.fromisoformat(project["start_date"])
        project_end = date.fromisoformat(project.get("actual_end") or project["end_date"])
        project_duration_days = max(1, (project_end - project_start).days)
        customer = registry.by_id("customer", "id", project["customer_id"])

        # Determine payment lag based on customer terms
        payment_terms = (customer or {}).get("payment_terms", "net_30")
        base_lag = {"due_on_receipt": 5, "net_15": 15, "net_30": 30, "net_45": 45, "net_60": 60}.get(payment_terms, 30)

        # Check for late payment event
        tag = project.get("narrative_tag", "")
        late_extra = 0
        for evt_list in events_by_tag.values():
            for evt in evt_list:
                if evt.get("type") == "late_payment" and evt.get("project_tag") == tag:
                    late_extra = evt.get("invoice_delay_days", 0) - base_lag

        # Short projects: 1 invoice. Medium: 2. Long: progress billing.
        if project_duration_days < 21:
            # Single invoice on completion
            inv_date = project_end
            _create_invoice(project, inv_date, contract, retention_pct, "final",
                            base_lag + max(0, late_extra), registry, rng, is_final=True)
        elif project_duration_days < 60:
            # 50% progress + final
            mid_date = project_start + timedelta(days=project_duration_days // 2)
            _create_invoice(project, mid_date, contract * 0.45, retention_pct, "progress",
                            base_lag, registry, rng)
            _create_invoice(project, project_end, contract * 0.55, retention_pct, "final",
                            base_lag + max(0, late_extra), registry, rng, is_final=True)
        else:
            # Monthly progress billing at 25%, 25%, 25%, 25% (retention held on each)
            n_invoices = max(3, min(6, project_duration_days // 30))
            pct_per = 1.0 / n_invoices
            for i in range(n_invoices):
                inv_date = project_start + timedelta(days=(project_duration_days * (i + 1)) // n_invoices)
                is_final = (i == n_invoices - 1)
                _create_invoice(project, inv_date, contract * pct_per, retention_pct,
                                "final" if is_final else "progress",
                                base_lag + (max(0, late_extra) if is_final else 0),
                                registry, rng, is_final=is_final)

        # Retention release: 30-90 days after project complete
        if retention_pct > 0:
            retention_total = _total_retention_held(project, registry)
            if retention_total > 0:
                release_date = project_end + timedelta(days=rng.randint(30, 90))
                _create_invoice(project, release_date, 0, 0, "retention",
                                base_lag, registry, rng, retention_override=retention_total)
                project["retention_released"] = True


def _create_invoice(project: dict, inv_date: date, gross_amount: float,
                     retention_pct: float, inv_type: str, payment_lag_days: int,
                     registry: Registry, rng: random.Random,
                     is_final: bool = False, retention_override: float = None) -> dict:
    inv_id = uid("INV-")
    count = len(registry.all("invoice")) + 1
    inv_number = f"INV-{count:04d}"

    if retention_override is not None:
        subtotal = 0.0
        retention = 0.0
        total_due = round_to_cents(retention_override)
    else:
        retention = round_to_cents(gross_amount * retention_pct)
        subtotal = round_to_cents(gross_amount)
        total_due = round_to_cents(subtotal - retention)

    due_date = inv_date + timedelta(days=payment_lag_days)

    # Actual payment: paid on or after due date, with some variance
    if rng.random() < 0.08:
        # 8% of invoices go significantly late
        paid_date = due_date + timedelta(days=rng.randint(15, 50))
    elif rng.random() < 0.15:
        paid_date = due_date + timedelta(days=rng.randint(1, 14))
    else:
        paid_date = due_date + timedelta(days=rng.randint(-5, 5))
        paid_date = max(paid_date, inv_date + timedelta(days=3))

    status = "paid"
    inv = registry.add("invoice", {
        "invoice_id": inv_id,
        "invoice_number": inv_number,
        "project_id": project["project_id"],
        "customer_id": project["customer_id"],
        "type": inv_type,
        "status": status,
        "issued_date": inv_date.isoformat(),
        "due_date": due_date.isoformat(),
        "subtotal": subtotal,
        "retention_held": retention,
        "tax": 0.0,
        "total_due": total_due,
        "notes": "",
    })

    # Payment record
    if total_due > 0:
        registry.add("payment", {
            "payment_id": uid("PAY-"),
            "invoice_id": inv_id,
            "project_id": project["project_id"],
            "customer_id": project["customer_id"],
            "amount": total_due,
            "method": rng.choices(["check", "ach", "credit_card"], weights=[0.5, 0.4, 0.1])[0],
            "reference": str(rng.randint(1001, 9999)),
            "received_date": paid_date.isoformat(),
            "deposited_date": (paid_date + timedelta(days=rng.randint(0, 2))).isoformat(),
        })

    return inv


def _total_retention_held(project: dict, registry: Registry) -> float:
    total = 0.0
    for inv in registry.filter("invoice", project_id=project["project_id"]):
        total += inv.get("retention_held", 0.0)
    return round_to_cents(total)


def generate_overhead_bills(cfg: dict, registry: Registry, rng: random.Random,
                             start_date: date, end_date: date) -> None:
    """Generate recurring monthly overhead bills."""
    events_cfg = cfg["events"]
    recurring = events_cfg.get("recurring_overhead", [])

    current = start_date.replace(day=1)
    while current <= end_date:
        for item in recurring:
            day = item.get("day_of_month", 1)
            try:
                bill_date = current.replace(day=day)
            except ValueError:
                bill_date = current.replace(day=28)

            if bill_date > end_date:
                continue

            if "amount_range" in item:
                amount = round_to_cents(rng.uniform(*item["amount_range"]))
            else:
                amount = round_to_cents(apply_variance(item["amount"], 0.05, rng))

            bill_id = uid("BILL-")
            due_date = bill_date + timedelta(days=30)

            registry.add("bill", {
                "bill_id": bill_id,
                "vendor_id": item["vendor_id"],
                "project_id": None,
                "job_id": None,
                "vendor_invoice_number": f"OH-{bill_date.strftime('%Y%m')}-{rng.randint(100,999)}",
                "status": "paid",
                "received_date": bill_date.isoformat(),
                "due_date": due_date.isoformat(),
                "total": amount,
                "paid_date": (bill_date + timedelta(days=rng.randint(5, 20))).isoformat(),
                "payment_method": rng.choice(["check", "ach"]),
                "check_number": str(rng.randint(1001, 9999)),
                "category": item.get("category", "overhead"),
            })

            registry.add("bill_line_item", {
                "line_id": uid("BLI-"),
                "bill_id": bill_id,
                "project_id": None,
                "job_id": None,
                "description": item["description"],
                "quantity": 1,
                "unit_cost": amount,
                "line_total": amount,
                "category": item.get("category", "overhead"),
            })

        # Advance month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    # One-time event overhead bills
    for evt in events_cfg.get("events", []):
        if evt.get("type") == "overhead_bill":
            bill_date = date.fromisoformat(evt["date"])
            if start_date <= bill_date <= end_date:
                amount = evt["amount"]
                bill_id = uid("BILL-")
                registry.add("bill", {
                    "bill_id": bill_id,
                    "vendor_id": evt["vendor_id"],
                    "project_id": None,
                    "job_id": None,
                    "vendor_invoice_number": f"OHE-{rng.randint(1000,9999)}",
                    "status": "paid",
                    "received_date": bill_date.isoformat(),
                    "due_date": (bill_date + timedelta(days=30)).isoformat(),
                    "total": round_to_cents(amount),
                    "paid_date": (bill_date + timedelta(days=rng.randint(5, 25))).isoformat(),
                    "payment_method": "check",
                    "check_number": str(rng.randint(1001, 9999)),
                    "category": evt.get("category", "overhead"),
                })
                registry.add("bill_line_item", {
                    "line_id": uid("BLI-"),
                    "bill_id": bill_id,
                    "project_id": None,
                    "job_id": None,
                    "description": evt["description"],
                    "quantity": 1,
                    "unit_cost": round_to_cents(amount),
                    "line_total": round_to_cents(amount),
                    "category": evt.get("category", "overhead"),
                })


def apply_variance(base: float, variance_pct: float, rng: random.Random = None) -> float:
    if rng is None:
        import random as _r
        rng = _r
    return rng.uniform(base * (1 - variance_pct), base * (1 + variance_pct))
