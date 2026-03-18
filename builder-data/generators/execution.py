"""Generate execution-layer data: time entries, bills, change orders."""
import random
from datetime import date, timedelta
from typing import Optional

from .base import Registry, uid, rand_between, round_to_cents, apply_variance
from .company import get_active_crew


def generate_execution(cfg: dict, registry: Registry, rng: random.Random,
                        events_by_tag: dict) -> None:
    """
    For each project that is 'awarded', simulate execution:
    - Advance project status through in_progress → punch_list → complete
    - Generate time entries day by day
    - Generate material/sub bills tied to job phases
    - Generate change orders for applicable narrative events
    """
    company_cfg = cfg["company"]
    projects = registry.all("project")

    for project in projects:
        if project["status"] not in ("awarded", "in_progress", "complete"):
            continue

        start = date.fromisoformat(project["start_date"])
        end = date.fromisoformat(project["end_date"])
        archetype = project["archetype"]
        arch = cfg["archetypes"][archetype]

        # Apply narrative event schedule delays
        tag = project.get("narrative_tag")
        extra_days = 0
        if tag and tag in events_by_tag:
            for evt in events_by_tag[tag]:
                if evt.get("type") == "schedule_delay":
                    extra_days += evt.get("schedule_delay_days", 0)
                elif evt.get("type") == "weather_delay":
                    extra_days += evt.get("schedule_delay_days", 0)

        actual_end = end + timedelta(days=extra_days)
        project["actual_start"] = start.isoformat()
        project["actual_end"] = actual_end.isoformat()
        project["status"] = "complete"

        jobs = registry.filter("job", project_id=project["project_id"])
        if not jobs:
            continue

        # Sort jobs by sort_order
        jobs_sorted = sorted(jobs, key=lambda j: j["sort_order"])

        # Assign each job a time window proportional to its cost share
        total_budget = sum(
            j["budgeted_labor_cost"] + j["budgeted_material_cost"] + j["budgeted_sub_cost"]
            for j in jobs_sorted
        ) or 1.0
        project_days = max(1, (actual_end - start).days)

        cursor = start
        for job in jobs_sorted:
            job_budget = job["budgeted_labor_cost"] + job["budgeted_material_cost"] + job["budgeted_sub_cost"]
            job_pct = job_budget / total_budget
            job_days = max(1, round(project_days * job_pct))
            job_end = min(cursor + timedelta(days=job_days), actual_end)

            job["status"] = "complete"
            job["actual_start"] = cursor.isoformat()
            job["actual_end"] = job_end.isoformat()

            # Variance: some jobs over, some under budget
            variance_factor = rng.uniform(0.82, 1.22)
            # Apply specific overruns from narrative events
            if tag and tag in events_by_tag:
                for evt in events_by_tag[tag]:
                    if (evt.get("type") == "budget_overrun"
                            and evt.get("phase_code") == job["code"]):
                        variance_factor *= (1 + evt.get("cost_overrun", 0) / max(job_budget, 1))

            # Labor time entries
            if job["budgeted_labor_cost"] > 0:
                _generate_time_entries(
                    job, project, cursor, job_end,
                    job["budgeted_labor_cost"] * variance_factor,
                    registry, rng, company_cfg
                )

            # Material bills
            if job["budgeted_material_cost"] > 0:
                _generate_material_bills(
                    job, project, cursor, job_end,
                    job["budgeted_material_cost"] * variance_factor,
                    registry, rng
                )

            # Sub bills
            if job["budgeted_sub_cost"] > 0:
                _generate_sub_bills(
                    job, project, cursor, job_end,
                    job["budgeted_sub_cost"] * variance_factor,
                    registry, rng
                )

            cursor = job_end

        # Change orders
        if tag and tag in events_by_tag:
            for evt in events_by_tag[tag]:
                if evt.get("change_order_submitted"):
                    _generate_change_order(project, evt, registry, rng)


def _generate_time_entries(job: dict, project: dict, start: date, end: date,
                            target_cost: float, registry: Registry,
                            rng: random.Random, company_cfg: dict) -> None:
    """Spread labor cost across working days in the job window."""
    working_days = [
        start + timedelta(days=i)
        for i in range((end - start).days + 1)
        if (start + timedelta(days=i)).weekday() < 5
    ]
    if not working_days:
        return

    # Get crew active during project
    project_start = date.fromisoformat(project["start_date"])
    active_employees = [
        e for e in registry.all("employee")
        if e.get("role") not in ("office_admin",)
        and e.get("burden_rate", 0) > 0
    ]
    if not active_employees:
        return

    # Distribute target_cost across working days
    daily_cost_target = target_cost / len(working_days)

    for work_date in working_days:
        # Randomly assign 1-3 employees per day
        n_crew = rng.randint(1, min(3, len(active_employees)))
        day_crew = rng.sample(active_employees, n_crew)

        for emp in day_crew:
            burden = emp.get("burden_rate", 35.0)
            if burden == 0:
                continue
            # Hours: target daily cost / burden rate / crew size
            target_hours = daily_cost_target / burden / n_crew
            hours = max(0.5, min(10, apply_variance(target_hours, 0.25, rng)))
            hours = round(hours * 2) / 2  # round to nearest 0.5

            # Occasional overtime (>8hrs on any day)
            ot_hours = max(0.0, hours - 8.0)
            reg_hours = min(8.0, hours)
            cost = round_to_cents(reg_hours * burden + ot_hours * burden * 1.5)

            registry.add("time_entry", {
                "entry_id": uid("TE-"),
                "employee_id": emp["id"],
                "project_id": project["project_id"],
                "job_id": job["job_id"],
                "date": work_date.isoformat(),
                "hours_regular": round(reg_hours, 2),
                "hours_overtime": round(ot_hours, 2),
                "cost": cost,
                "notes": f"{job['name']} work",
            })


def _generate_material_bills(job: dict, project: dict, start: date, end: date,
                              target_cost: float, registry: Registry,
                              rng: random.Random) -> None:
    """Generate 1-4 material purchase bills for a job phase."""
    n_bills = rng.randint(1, 4)
    # Most materials come in early in the phase
    supplier_ids = [
        v["id"] for v in registry.all("vendor")
        if v.get("type") in ("supplier",)
    ]
    if not supplier_ids:
        return

    amounts = _split_amount(target_cost, n_bills, rng)
    for i, amount in enumerate(amounts):
        # Earlier bills in phase = more likely early dates
        bill_date = start + timedelta(days=rng.randint(0, max(1, (end - start).days // 2)))
        vendor_id = rng.choice(supplier_ids)

        bill_id = uid("BILL-")
        due_date = bill_date + timedelta(days=30)

        registry.add("bill", {
            "bill_id": bill_id,
            "vendor_id": vendor_id,
            "project_id": project["project_id"],
            "job_id": job["job_id"],
            "vendor_invoice_number": f"SI-{rng.randint(10000, 99999)}",
            "status": "paid",
            "received_date": bill_date.isoformat(),
            "due_date": due_date.isoformat(),
            "total": round_to_cents(amount),
            "paid_date": (bill_date + timedelta(days=rng.randint(15, 40))).isoformat(),
            "payment_method": rng.choice(["check", "ach"]),
            "check_number": str(rng.randint(1001, 9999)) if rng.random() > 0.4 else None,
            "category": "material",
        })

        registry.add("bill_line_item", {
            "line_id": uid("BLI-"),
            "bill_id": bill_id,
            "project_id": project["project_id"],
            "job_id": job["job_id"],
            "description": f"{job['name']} materials",
            "quantity": 1,
            "unit_cost": round_to_cents(amount),
            "line_total": round_to_cents(amount),
            "category": "material",
        })


def _generate_sub_bills(job: dict, project: dict, start: date, end: date,
                         target_cost: float, registry: Registry,
                         rng: random.Random) -> None:
    """Generate subcontractor invoices for a job phase."""
    sub_type = job.get("sub_vendor_type")
    if not sub_type:
        return

    trade = sub_type
    candidates = [
        v for v in registry.all("vendor")
        if v.get("type") == "subcontractor" and v.get("trade") == trade
    ]
    if not candidates:
        return

    vendor = rng.choice(candidates)
    # Subs typically bill in 1-2 invoices (mobilization + final)
    n_bills = rng.choices([1, 2], weights=[0.4, 0.6])[0]
    amounts = _split_amount(target_cost, n_bills, rng, first_pct=0.5)

    for i, amount in enumerate(amounts):
        bill_date = start + timedelta(days=i * max(1, (end - start).days // 2))
        bill_date = min(bill_date, end)
        due_date = bill_date + timedelta(days=15)

        bill_id = uid("BILL-")
        registry.add("bill", {
            "bill_id": bill_id,
            "vendor_id": vendor["id"],
            "project_id": project["project_id"],
            "job_id": job["job_id"],
            "vendor_invoice_number": f"{vendor['id']}-{rng.randint(100, 999)}",
            "status": "paid",
            "received_date": bill_date.isoformat(),
            "due_date": due_date.isoformat(),
            "total": round_to_cents(amount),
            "paid_date": (bill_date + timedelta(days=rng.randint(10, 25))).isoformat(),
            "payment_method": "check",
            "check_number": str(rng.randint(1001, 9999)),
            "category": "subcontractor",
        })

        registry.add("bill_line_item", {
            "line_id": uid("BLI-"),
            "bill_id": bill_id,
            "project_id": project["project_id"],
            "job_id": job["job_id"],
            "description": f"{job['name']} — {vendor['name']} {'mobilization' if i == 0 else 'final invoice'}",
            "quantity": 1,
            "unit_cost": round_to_cents(amount),
            "line_total": round_to_cents(amount),
            "category": "subcontractor",
        })


def _generate_change_order(project: dict, evt: dict, registry: Registry,
                            rng: random.Random) -> None:
    cost_impact = evt.get("cost_impact", evt.get("cost_overrun", 0))
    approved_amount = evt.get("change_order_approved_amount", cost_impact)

    co_id = uid("CO-")
    co_list = registry.filter("change_order", project_id=project["project_id"])
    co_number = f"CO-{len(co_list) + 1:03d}"

    registry.add("change_order", {
        "co_id": co_id,
        "project_id": project["project_id"],
        "co_number": co_number,
        "status": "approved" if approved_amount > 0 else "declined",
        "description": evt.get("description", "Change order"),
        "cost_impact": round_to_cents(cost_impact),
        "approved_amount": round_to_cents(approved_amount),
        "schedule_impact_days": evt.get("schedule_delay_days", 0),
        "requested_by": "contractor",
        "approved_date": evt.get("date"),
    })


def _split_amount(total: float, n: int, rng: random.Random,
                   first_pct: float = None) -> list[float]:
    """Split total into n parts roughly evenly, with optional first_pct for first chunk."""
    if n == 1:
        return [total]
    if first_pct and n == 2:
        first = total * first_pct
        return [round_to_cents(first), round_to_cents(total - first)]

    splits = sorted([rng.random() for _ in range(n - 1)] + [0, 1])
    amounts = [round_to_cents(total * (splits[i + 1] - splits[i])) for i in range(n)]
    # Fix rounding: make last item absorb any penny difference
    diff = round_to_cents(total - sum(amounts))
    amounts[-1] = round_to_cents(amounts[-1] + diff)
    return amounts


def apply_variance(base: float, variance_pct: float, rng: random.Random = None) -> float:
    if rng is None:
        import random as _r
        rng = _r
    lo = base * (1 - variance_pct)
    hi = base * (1 + variance_pct)
    return rng.uniform(lo, hi)
