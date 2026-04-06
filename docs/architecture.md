# Architecture

## Pipeline

```
Connector → canonical dict → Detector → [PatternResult] → Interpreter → [Finding] → Output → JSON
```

## Components

- `connectors/` — input adapters. `ScenarioConnector` loads JSON files; `ManualConnector` accepts a dict. Both must implement `source_descriptor()` and `load()` from `base.py`.
- `engine/rules.py` — 5 detection functions. Each receives the canonical payload dict and returns a `PatternResult` or `None`. The `PATTERN_DETECTORS` list is the registry — append to extend.
- `engine/detector.py` — iterates `PATTERN_DETECTORS`, collects non-empty results.
- `engine/interpreter.py` — one interpreter per pattern; converts a `PatternResult` into a `Finding` with actionable `ImprovementTask` objects.
- `engine/output.py` — assembles final JSON with metadata and findings list.
- `engine/models.py` — all dataclasses (`Task`, `PullRequest`, `Service`, `PatternResult`, `Finding`, `ImprovementTask`, etc.).
- `engine/contracts.py` — allowed values for categories, modes, statuses, priorities (used for validation).

## Adding a New Pattern

1. Add a detector function in `engine/rules.py` and append it to `PATTERN_DETECTORS`.
2. Add a corresponding interpreter in `engine/interpreter.py` and register it in the interpreter dispatch map.
3. Add unit tests in `tests/test_rules.py` and a scenario JSON in `scenarios/` with an end-to-end test in `tests/test_scenarios.py`.

## Canonical Payload Shape

```json
{
  "source": { "category": "work_tracking|code_collaboration|service_context", "mode": "live|scenario|user_provided", "product": "jira|github|gitlab|manual" },
  "tasks": [
    {
      "id": "T-001", "title": "...", "status": "open|in_progress|done|blocked",
      "priority": "critical|high|medium|low|null",
      "owner": "name|null", "team": "name|null", "service": "service_id|null",
      "done_criteria": "text|null", "success_metric": "text|null",
      "age_days": 12, "in_report": true,
      "labels": ["label"],
      "history": [{ "event": "owner_change|status_change|team_transfer|comment|label_change", "from": "x", "to": "y", "days_ago": 5 }]
    }
  ],
  "pull_requests": [{ "id": "PR-001", "title": "...", "author": "bob", "reviewers": [], "status": "open|merged|closed", "linked_task_id": "T-001", "age_days": 3 }],
  "services": [{ "id": "svc", "name": "...", "owner_team": "team|null", "criticality": "p0|p1|p2" }]
}
```

## Detection Thresholds

| Constant | Value | Used in |
|---|---|---|
| `OWNERSHIP_CHANGE_THRESHOLD` | 2 | `orphan_work` |
| `CIRCULATION_CHANGES_THRESHOLD` | 3 | `circulating_work` |
| `CIRCULATION_AGE_THRESHOLD` | 14 days | `circulating_work` |
| `STALE_UNTRACKED_THRESHOLD` | 7 days | `untracked_work_dies` |
| `PRIORITY_SPREAD_THRESHOLD` | 3 | `priority_translation_failure` |
