"""
Fallback interpreter: converts a PatternResult into a structured Finding.
No LLM. All text is deterministic and pattern-specific.
"""
from __future__ import annotations

from engine.models import Finding, ImprovementTask, PatternResult


def interpret(result: PatternResult) -> Finding:
    interpreters = {
        "orphan_work": _orphan_work,
        "undefined_outcome": _undefined_outcome,
        "priority_translation_failure": _priority_translation_failure,
        "untracked_work_dies": _untracked_work_dies,
        "circulating_work": _circulating_work,
    }
    fn = interpreters.get(result.pattern)
    if fn is None:
        raise ValueError(f"No interpreter registered for pattern: {result.pattern}")
    return fn(result)


# ---------------------------------------------------------------------------
# Per-pattern interpreters
# ---------------------------------------------------------------------------

def _orphan_work(result: PatternResult) -> Finding:
    ctx = result.context
    tasks_no_owner: list[str] = ctx.get("tasks_no_owner", [])
    services_no_team: list[str] = ctx.get("services_no_owner_team", [])
    tasks_churning: list[str] = ctx.get("tasks_churning", [])
    prs_no_reviewer: list[str] = ctx.get("prs_no_reviewer", [])

    # Evidence-driven interpretation
    parts: list[str] = []
    if tasks_no_owner and services_no_team:
        parts.append(
            f"{', '.join(tasks_no_owner)} {'has' if len(tasks_no_owner) == 1 else 'have'} "
            f"no owner and no team, and "
            f"{'their' if len(tasks_no_owner) > 1 else 'its'} linked "
            f"{'services' if len(services_no_team) > 1 else 'service'} "
            f"({', '.join(services_no_team)}) also {'have' if len(services_no_team) > 1 else 'has'} "
            f"no owner_team — there is no accountability at either the task or service level"
        )
    elif tasks_no_owner:
        parts.append(
            f"{', '.join(tasks_no_owner)} {'has' if len(tasks_no_owner) == 1 else 'have'} "
            "no owner and no team — no one is accountable for their completion"
        )
    elif services_no_team:
        parts.append(
            f"{'Services' if len(services_no_team) > 1 else 'Service'} "
            f"{', '.join(services_no_team)} "
            f"{'have' if len(services_no_team) > 1 else 'has'} no owner_team, "
            "leaving linked tasks structurally unaccountable"
        )
    if tasks_churning:
        parts.append(
            f"{', '.join(tasks_churning)} {'has' if len(tasks_churning) == 1 else 'have'} "
            "changed ownership repeatedly without settling on a responsible party"
        )
    if prs_no_reviewer:
        parts.append(
            f"{', '.join(prs_no_reviewer)} {'is' if len(prs_no_reviewer) == 1 else 'are'} "
            "open with no reviewer assigned — review is blocked with no owner"
        )
    interpretation = ". ".join(parts) + "." if parts else "Work items have no accountable owner."

    # Specific, entity-level improvement actions
    improvements: list[ImprovementTask] = []

    for tid in tasks_no_owner:
        improvements.append(ImprovementTask(
            action=f"Assign a directly responsible owner to {tid} before it advances further",
            owner_hint="team lead",
            urgency="immediate",
        ))

    for svc in services_no_team:
        improvements.append(ImprovementTask(
            action=f"Assign an owner_team to {svc} to establish service-level accountability",
            owner_hint="engineering manager",
            urgency="immediate",
        ))

    for tid in tasks_churning:
        improvements.append(ImprovementTask(
            action=f"Resolve ownership for {tid}: declare a single accountable person and do not transfer again without a documented reason",
            owner_hint="engineering manager",
            urgency="short_term",
        ))

    for pid in prs_no_reviewer:
        improvements.append(ImprovementTask(
            action=f"Assign at least one reviewer to {pid} or close it if it is no longer active",
            owner_hint="tech lead",
            urgency="immediate",
        ))

    if not tasks_no_owner and not prs_no_reviewer:
        improvements.append(ImprovementTask(
            action="Enforce an owner-required policy: block tasks from moving to in_progress without a named owner",
            owner_hint="engineering manager",
            urgency="short_term",
        ))

    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=(
            f"{len(result.matched_ids)} work item(s) have no clear owner, "
            "team, or accountable service."
        ),
        evidence=result.signals,
        interpretation=interpretation,
        suggested_improvements=improvements,
    )


def _undefined_outcome(result: PatternResult) -> Finding:
    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=(
            f"{len(result.matched_ids)} active task(s) have no done criteria "
            "or success metric defined."
        ),
        evidence=result.signals,
        interpretation=(
            "Work without a definition of done runs indefinitely. Teams ship features "
            "without knowing whether the outcome was achieved. This makes retrospectives "
            "meaningless, makes prioritization guesswork, and allows low-value work to "
            "consume sprint capacity indefinitely."
        ),
        suggested_improvements=[
            ImprovementTask(
                action=(
                    "Add done_criteria to every active task before it advances "
                    "to in_progress — enforce this at the task creation step"
                ),
                owner_hint="task owner",
                urgency="immediate",
            ),
            ImprovementTask(
                action=(
                    "Define a success_metric for each task that has a measurable "
                    "business or system impact (e.g. latency, error rate, conversion)"
                ),
                owner_hint="product manager",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Add an outcome review gate to the sprint review: "
                    "tasks without a verified success_metric cannot be marked done"
                ),
                owner_hint="engineering manager",
                urgency="ongoing",
            ),
        ],
    )


def _priority_translation_failure(result: PatternResult) -> Finding:
    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=(
            f"{len(result.matched_ids)} task(s) show priority inconsistency — "
            "missing priority, urgency/priority mismatch, or spread across a single service."
        ),
        evidence=result.signals,
        interpretation=(
            "When priority is absent or contradictory, teams cannot sequence work "
            "correctly. High-value work gets delayed by lower-value noise. "
            "A single service with tasks at every priority level means no task "
            "is actually prioritized — everything is equally important, which means "
            "nothing is."
        ),
        suggested_improvements=[
            ImprovementTask(
                action=(
                    "Assign an explicit priority to every active task that currently "
                    "has none — use the service criticality as a baseline if uncertain"
                ),
                owner_hint="team lead",
                urgency="immediate",
            ),
            ImprovementTask(
                action=(
                    "Align task priority with label urgency signals: "
                    "any task with a 'critical' or 'blocker' label must have "
                    "priority='critical' or priority='high'"
                ),
                owner_hint="product manager",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Establish a priority review cadence: at the start of each sprint, "
                    "confirm that the highest-priority tasks have a clear execution path "
                    "(owner, service, done_criteria)"
                ),
                owner_hint="engineering manager",
                urgency="ongoing",
            ),
        ],
    )


def _untracked_work_dies(result: PatternResult) -> Finding:
    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=(
            f"{len(result.matched_ids)} active task(s) are not tracked in reports "
            "or have no visible metric — invisible to the team."
        ),
        evidence=result.signals,
        interpretation=(
            "Invisible work cannot be prioritized, escalated, or completed reliably. "
            "It creates hidden risk: team members spend time on work that leadership "
            "cannot see, cannot support, and will not protect during re-prioritization. "
            "Eventually this work dies silently, wasting the effort already invested."
        ),
        suggested_improvements=[
            ImprovementTask(
                action=(
                    "Add all active tasks to the team's weekly report immediately — "
                    "if a task cannot be described in the report, it should not be active"
                ),
                owner_hint="team lead",
                urgency="immediate",
            ),
            ImprovementTask(
                action=(
                    "Define a success_metric for each task that lacks one; "
                    "link every task to a service or product area for traceability"
                ),
                owner_hint="task owner",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Require service linkage and report inclusion as mandatory fields "
                    "when creating any new task"
                ),
                owner_hint="engineering manager",
                urgency="ongoing",
            ),
        ],
    )


def _circulating_work(result: PatternResult) -> Finding:
    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=(
            f"{len(result.matched_ids)} task(s) are moving repeatedly "
            "without converging toward completion."
        ),
        evidence=result.signals,
        interpretation=(
            "Circulating work indicates unresolved blockers, unclear exit criteria, "
            "or a dependency that nobody owns. Each status change consumes team attention "
            "without producing value. Left unaddressed, circulating tasks become permanent "
            "fixtures in the backlog, eroding team trust in the planning process."
        ),
        suggested_improvements=[
            ImprovementTask(
                action=(
                    "For each circulating task, explicitly identify and document the "
                    "blocking reason — if no blocker exists, define the next concrete step"
                ),
                owner_hint="task owner",
                urgency="immediate",
            ),
            ImprovementTask(
                action=(
                    "Set a hard decision deadline for tasks older than 14 days: "
                    "either resolve the blocker within 3 days or close the task"
                ),
                owner_hint="team lead",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Add a convergence check to the sprint review: "
                    "any task that changed status more than twice in a sprint "
                    "requires a root cause discussion before the next sprint starts"
                ),
                owner_hint="engineering manager",
                urgency="ongoing",
            ),
        ],
    )
