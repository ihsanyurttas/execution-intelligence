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
    return Finding(
        pattern=result.pattern,
        issue=(
            f"{len(result.matched_ids)} work item(s) have no clear owner, "
            "team, or accountable service."
        ),
        evidence=result.signals,
        interpretation=(
            "Orphan work accumulates invisibly. Without a named owner, no one "
            "escalates, no one prioritizes, and the work silently stalls or dies. "
            "When ownership is also absent at the service level, the gap compounds: "
            "even structural accountability is missing."
        ),
        suggested_improvements=[
            ImprovementTask(
                action=(
                    f"Assign an explicit owner to each of the {len(result.matched_ids)} "
                    "unowned items before the next planning session"
                ),
                owner_hint="team lead",
                urgency="immediate",
            ),
            ImprovementTask(
                action=(
                    "Define an owner_team for every service that currently lacks one; "
                    "block new tasks from being linked to ownerless services"
                ),
                owner_hint="engineering manager",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Add a reviewer-required policy to the code review process "
                    "so that PRs cannot remain open without a reviewer for more than 24 hours"
                ),
                owner_hint="tech lead",
                urgency="short_term",
            ),
            ImprovementTask(
                action=(
                    "Run a weekly ownership audit: any task older than 3 days "
                    "without an owner is escalated automatically"
                ),
                owner_hint="engineering manager",
                urgency="ongoing",
            ),
        ],
    )


def _undefined_outcome(result: PatternResult) -> Finding:
    return Finding(
        pattern=result.pattern,
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
