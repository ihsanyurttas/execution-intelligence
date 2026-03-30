"""
Domain model dataclasses.

Input entities (Task, PullRequest, Service, SourceDescriptor) document
the canonical payload shape and are used as type references.

Output entities (PatternResult, Finding, ImprovementTask) are instantiated
by rules.py and interpreter.py.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------

@dataclass
class SourceDescriptor:
    category: str           # work_tracking | code_collaboration | service_context
    mode: str               # live | scenario | user_provided
    product: str            # jira | github | gitlab | manual


# ---------------------------------------------------------------------------
# Input entities (canonical payload shape)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    id: str
    title: str
    status: str                         # open | in_progress | done | blocked
    age_days: int
    priority: Optional[str] = None      # critical | high | medium | low | None
    owner: Optional[str] = None
    team: Optional[str] = None
    service: Optional[str] = None       # service id reference
    done_criteria: Optional[str] = None
    success_metric: Optional[str] = None
    in_report: bool = True              # False = not visible in any team report
    labels: list[str] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)
    # history events: {event, from, to, days_ago}
    # event types: status_change | owner_change | team_transfer


@dataclass
class PullRequest:
    id: str
    title: str
    author: str
    status: str                         # open | merged | closed
    age_days: int
    reviewers: list[str] = field(default_factory=list)
    linked_task_id: Optional[str] = None


@dataclass
class Service:
    id: str
    name: str
    owner_team: Optional[str] = None
    criticality: Optional[str] = None  # p0 | p1 | p2


# ---------------------------------------------------------------------------
# Engine output types
# ---------------------------------------------------------------------------

@dataclass
class PatternResult:
    pattern: str
    matched_ids: list[str]  # task/PR ids that triggered this pattern
    signals: list[str]      # human-readable observations from the input
    severity: str = "medium"  # high | medium | low


@dataclass
class ImprovementTask:
    action: str
    owner_hint: str         # role or person who should act
    urgency: str            # immediate | short_term | ongoing


@dataclass
class Finding:
    pattern: str
    severity: str           # high | medium | low
    issue: str
    evidence: list[str]
    interpretation: str
    suggested_improvements: list[ImprovementTask]
