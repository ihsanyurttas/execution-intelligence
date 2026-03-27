"""
Deterministic pattern detection rules.

One function per pattern. Each returns None (no match) or a PatternResult.
Rules operate directly on the canonical payload dict — no ORM, no framework.

Add a new pattern by writing a new detect_* function and appending it to
PATTERN_DETECTORS.
"""
from __future__ import annotations
from collections import defaultdict

from engine.contracts import ACTIVE_TASK_STATUSES
from engine.models import PatternResult


# ---------------------------------------------------------------------------
# Thresholds (explicit, not hidden in magic)
# ---------------------------------------------------------------------------

OWNERSHIP_CHANGE_THRESHOLD = 2      # >= this many changes → orphan signal
CIRCULATION_CHANGES_THRESHOLD = 3   # >= this many status changes → circulating
CIRCULATION_AGE_THRESHOLD = 14      # days old + has history → circulating
STALE_UNTRACKED_THRESHOLD = 7       # days old + no service + no metric → dying
PRIORITY_SPREAD_THRESHOLD = 3       # distinct priorities in same service → failure

URGENCY_LABELS = {"critical", "urgent", "p0", "blocker"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active(task: dict) -> bool:
    return task.get("status") in ACTIVE_TASK_STATUSES


def _label(task: dict, tid: str) -> str:
    return f"{tid} '{task.get('title', '')}'"


# ---------------------------------------------------------------------------
# 1. orphan_work
# ---------------------------------------------------------------------------

def detect_orphan_work(payload: dict) -> PatternResult | None:
    """
    Signals:
    - Active task has no owner AND no team
    - Active task is linked to a service that has no owner_team
    - Active task has >= OWNERSHIP_CHANGE_THRESHOLD ownership/team change events
    - Open PR has no reviewers assigned
    """
    tasks = payload.get("tasks", [])
    prs = payload.get("pull_requests", [])
    services_by_id = {s["id"]: s for s in payload.get("services", [])}

    matched_ids: list[str] = []
    signals: list[str] = []

    for task in tasks:
        if not _active(task):
            continue
        tid = task["id"]

        if not task.get("owner") and not task.get("team"):
            matched_ids.append(tid)
            signals.append(f"Task {_label(task, tid)} has no owner and no team")

        svc_id = task.get("service")
        if svc_id:
            svc = services_by_id.get(svc_id)
            if svc and not svc.get("owner_team"):
                if tid not in matched_ids:
                    matched_ids.append(tid)
                signals.append(
                    f"Task {tid} is linked to service '{svc_id}' which has no owner team"
                )

        ownership_events = [
            h for h in task.get("history", [])
            if h.get("event") in ("owner_change", "team_transfer")
        ]
        if len(ownership_events) >= OWNERSHIP_CHANGE_THRESHOLD:
            if tid not in matched_ids:
                matched_ids.append(tid)
            signals.append(
                f"Task {tid} has {len(ownership_events)} ownership/team changes — "
                "responsibility is not settling"
            )

    for pr in prs:
        if pr.get("status") == "open" and not pr.get("reviewers"):
            pid = pr["id"]
            matched_ids.append(pid)
            signals.append(
                f"PR {pid} '{pr.get('title', '')}' is open with no reviewers assigned"
            )

    if not signals:
        return None

    return PatternResult(
        pattern="orphan_work",
        matched_ids=list(dict.fromkeys(matched_ids)),
        signals=signals,
    )


# ---------------------------------------------------------------------------
# 2. undefined_outcome
# ---------------------------------------------------------------------------

def detect_undefined_outcome(payload: dict) -> PatternResult | None:
    """
    Signals:
    - Active task is missing done_criteria
    - Active task is missing success_metric
    """
    tasks = payload.get("tasks", [])
    matched_ids: list[str] = []
    signals: list[str] = []

    for task in tasks:
        if not _active(task):
            continue
        tid = task["id"]

        missing = []
        if not task.get("done_criteria"):
            missing.append("done_criteria")
        if not task.get("success_metric"):
            missing.append("success_metric")

        if missing:
            matched_ids.append(tid)
            signals.append(
                f"Task {_label(task, tid)} is missing: {', '.join(missing)}"
            )

    if not signals:
        return None

    return PatternResult(
        pattern="undefined_outcome",
        matched_ids=matched_ids,
        signals=signals,
    )


# ---------------------------------------------------------------------------
# 3. priority_translation_failure
# ---------------------------------------------------------------------------

def detect_priority_translation_failure(payload: dict) -> PatternResult | None:
    """
    Signals:
    - Active task has no priority set
    - Active task has urgency labels but priority is not critical/high (mismatch)
    - A single service has tasks with >= PRIORITY_SPREAD_THRESHOLD distinct priorities
    """
    tasks = payload.get("tasks", [])
    matched_ids: list[str] = []
    signals: list[str] = []

    by_service: dict[str, list[dict]] = defaultdict(list)

    for task in tasks:
        if not _active(task):
            continue
        tid = task["id"]
        priority = task.get("priority")
        labels = set(task.get("labels", []))

        if not priority:
            matched_ids.append(tid)
            signals.append(
                f"Task {_label(task, tid)} is active with no priority set"
            )
        elif labels & URGENCY_LABELS and priority not in ("critical", "high"):
            matched_ids.append(tid)
            signals.append(
                f"Task {tid} carries urgency labels "
                f"{labels & URGENCY_LABELS} but priority is '{priority}'"
            )

        svc = task.get("service")
        if svc:
            by_service[svc].append(task)

    for service, svc_tasks in by_service.items():
        priorities = {t.get("priority") for t in svc_tasks if t.get("priority")}
        if len(priorities) >= PRIORITY_SPREAD_THRESHOLD:
            for t in svc_tasks:
                if t["id"] not in matched_ids:
                    matched_ids.append(t["id"])
            signals.append(
                f"Service '{service}' has {len(priorities)} distinct priority levels "
                f"across active tasks: {sorted(p for p in priorities if p)}"
            )

    if not signals:
        return None

    return PatternResult(
        pattern="priority_translation_failure",
        matched_ids=list(dict.fromkeys(matched_ids)),
        signals=signals,
    )


# ---------------------------------------------------------------------------
# 4. untracked_work_dies
# ---------------------------------------------------------------------------

def detect_untracked_work_dies(payload: dict) -> PatternResult | None:
    """
    Signals:
    - Active task has in_report=False (explicitly excluded from reports)
    - Active task has no success_metric AND no service linkage AND is old
    """
    tasks = payload.get("tasks", [])
    matched_ids: list[str] = []
    signals: list[str] = []

    for task in tasks:
        if not _active(task):
            continue
        tid = task["id"]

        if task.get("in_report") is False:
            matched_ids.append(tid)
            signals.append(
                f"Task {_label(task, tid)} is active but not included in any team report"
            )

        no_metric = not task.get("success_metric")
        no_service = not task.get("service")
        age = task.get("age_days", 0)
        if no_metric and no_service and age >= STALE_UNTRACKED_THRESHOLD:
            if tid not in matched_ids:
                matched_ids.append(tid)
            signals.append(
                f"Task {tid} has no tracking metric, no service context, "
                f"and is {age} days old — invisible to the system"
            )

    if not signals:
        return None

    return PatternResult(
        pattern="untracked_work_dies",
        matched_ids=list(dict.fromkeys(matched_ids)),
        signals=signals,
    )


# ---------------------------------------------------------------------------
# 5. circulating_work
# ---------------------------------------------------------------------------

def detect_circulating_work(payload: dict) -> PatternResult | None:
    """
    Signals:
    - Active task has >= CIRCULATION_CHANGES_THRESHOLD status_change events
    - Active task status has returned to a previously visited state (bounce)
    - Active task is >= CIRCULATION_AGE_THRESHOLD days old with movement history
    """
    tasks = payload.get("tasks", [])
    matched_ids: list[str] = []
    signals: list[str] = []

    for task in tasks:
        if not _active(task):
            continue
        tid = task["id"]
        history = task.get("history", [])
        status_changes = [h for h in history if h.get("event") == "status_change"]
        age = task.get("age_days", 0)

        if len(status_changes) >= CIRCULATION_CHANGES_THRESHOLD:
            matched_ids.append(tid)
            signals.append(
                f"Task {_label(task, tid)} has {len(status_changes)} status changes "
                "without reaching completion"
            )
            continue

        # Detect status bounce: a status appears as "to" after already being left
        visited: set[str] = set()
        bounced = False
        for change in status_changes:
            from_status = change.get("from", "")
            to_status = change.get("to", "")
            if from_status:
                visited.add(from_status)
            if to_status and to_status in visited:
                bounced = True
                break

        if bounced:
            if tid not in matched_ids:
                matched_ids.append(tid)
            signals.append(
                f"Task {tid} returned to a previously visited status — work is cycling"
            )

        # Old task still moving
        if age >= CIRCULATION_AGE_THRESHOLD and len(history) > 0:
            if tid not in matched_ids:
                matched_ids.append(tid)
            signals.append(
                f"Task {tid} is {age} days old with {len(history)} history events "
                "but has not completed"
            )

    if not signals:
        return None

    return PatternResult(
        pattern="circulating_work",
        matched_ids=list(dict.fromkeys(matched_ids)),
        signals=signals,
    )


# ---------------------------------------------------------------------------
# Registry — extend by appending here, nothing else required
# ---------------------------------------------------------------------------

PATTERN_DETECTORS = [
    detect_orphan_work,
    detect_undefined_outcome,
    detect_priority_translation_failure,
    detect_untracked_work_dies,
    detect_circulating_work,
]
