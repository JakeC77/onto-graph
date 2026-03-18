"""Apply narrative events to the registry — crew changes, pricing changes, etc."""
from datetime import date, timedelta

from .base import Registry, uid, round_to_cents


def apply_narrative_events(cfg: dict, registry: Registry) -> dict:
    """
    Process all events from config/events.yaml.
    Returns a dict of {project_tag: [events]} for downstream use.
    Also applies crew changes, pricing changes, and other mutations.
    """
    events_cfg = cfg["events"]
    events = events_cfg.get("events", [])

    by_tag: dict[str, list] = {}

    for evt in events:
        evt_type = evt.get("type")
        evt_date = date.fromisoformat(evt["date"])

        # Index by project_tag for downstream generators
        for tag_field in ("project_tag", "affected_project_tags"):
            tags = evt.get(tag_field)
            if not tags:
                continue
            if isinstance(tags, str):
                tags = [tags]
            for tag in tags:
                by_tag.setdefault(tag, []).append(evt)

        # ── Crew events ──────────────────────────────────────────────────────
        if evt_type == "new_hire":
            emp_id = evt.get("employee_id")
            emp = registry.by_id("employee", "id", emp_id)
            if emp and emp.get("status") != "active":
                emp["status"] = "active"

        elif evt_type == "employee_departure":
            emp_id = evt.get("employee_id")
            emp = registry.by_id("employee", "id", emp_id)
            if emp:
                emp["status"] = "terminated"
                emp["termination_date"] = evt["date"]

        elif evt_type == "promotion":
            emp_id = evt.get("employee_id")
            emp = registry.by_id("employee", "id", emp_id)
            if emp:
                emp["role"] = "journeyman"

        # ── Pricing events ────────────────────────────────────────────────────
        elif evt_type == "pricing_change":
            # Record the pricing change for use during estimate generation
            registry.add("pricing_change", {
                "event_id": evt["id"],
                "effective_date": evt["date"],
                "applies_to": evt.get("applies_to"),
                "old_bill_rate": evt.get("old_bill_rate"),
                "new_bill_rate": evt.get("new_bill_rate"),
                "notes": evt.get("notes", ""),
            })

        # ── Insurance / compliance ────────────────────────────────────────────
        elif evt_type == "sub_insurance_renewed":
            vendor_id = evt.get("vendor_id")
            vendor = registry.by_id("vendor", "id", vendor_id)
            if vendor:
                vendor["insurance_expiry"] = evt.get("new_expiry")

        # ── Line of credit draws ──────────────────────────────────────────────
        elif evt_type == "loc_draw":
            registry.add("loc_event", {
                "event_id": evt["id"],
                "date": evt["date"],
                "amount": evt["amount"],
                "type": "draw",
                "description": evt["description"],
            })

        # ── Supplier account opens ────────────────────────────────────────────
        elif evt_type == "supplier_account":
            vendor_id = evt.get("vendor_id")
            vendor = registry.by_id("vendor", "id", vendor_id)
            if vendor:
                vendor["credit_limit"] = evt.get("credit_limit", 0)
                vendor["account_opened"] = evt["date"]

        # ── Overtime spikes ───────────────────────────────────────────────────
        elif evt_type == "overtime_spike":
            registry.add("overtime_event", {
                "event_id": evt["id"],
                "start_date": evt["date"],
                "duration_weeks": evt.get("duration_weeks", 1),
                "ot_hours_per_week_per_person": evt.get("ot_hours_per_week_per_person", 8),
                "affected_employees": evt.get("affected_employees", []),
                "description": evt.get("description", ""),
            })

    return by_tag


def generate_narrative_time_entries(cfg: dict, registry: Registry, rng) -> None:
    """
    Generate the overtime spike time entries from EVT-018 (Vega departure).
    These are standalone entries not tied to a specific project phase — they
    represent the general overwork across all active projects during the period.
    """
    for ot_evt in registry.all("overtime_event"):
        start = date.fromisoformat(ot_evt["start_date"])
        weeks = ot_evt["duration_weeks"]
        ot_per_person = ot_evt["ot_hours_per_week_per_person"]
        affected = ot_evt["affected_employees"]

        # Find active projects during this window
        end = start + timedelta(weeks=weeks)
        active_projects = [
            p for p in registry.all("project")
            if p.get("actual_start") and p.get("actual_end")
            and date.fromisoformat(p["actual_start"]) <= end
            and date.fromisoformat(p["actual_end"]) >= start
        ]
        if not active_projects:
            return

        for emp_id in affected:
            emp = registry.by_id("employee", "id", emp_id)
            if not emp:
                continue
            burden = emp.get("burden_rate", 35.0)

            current = start
            while current < end:
                if current.weekday() < 5:  # weekday
                    project = rng.choice(active_projects)
                    jobs = registry.filter("job", project_id=project["project_id"])
                    job = rng.choice(jobs) if jobs else None

                    # Extra OT hours that week (spread daily)
                    daily_ot = round(ot_per_person / 5, 1)
                    ot_cost = round_to_cents(daily_ot * burden * 1.5)

                    registry.add("time_entry", {
                        "entry_id": uid("TE-"),
                        "employee_id": emp_id,
                        "project_id": project["project_id"],
                        "job_id": job["job_id"] if job else None,
                        "date": current.isoformat(),
                        "hours_regular": 0.0,
                        "hours_overtime": daily_ot,
                        "cost": ot_cost,
                        "notes": f"OT coverage — crew gap [{ot_evt['event_id']}]",
                    })
                current += timedelta(days=1)
