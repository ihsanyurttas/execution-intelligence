# Execution Intelligence Engine

A source-agnostic engine that detects execution failure patterns in engineering teams and produces structured findings with actionable improvement tasks.

## What this is

Engineering teams observe symptoms — blocked work, missed deadlines, unclear priorities. This engine looks for the underlying patterns that generate those symptoms and recommends the highest-impact corrective actions.

This is a deterministic prototype. No LLM, no database, no web server.

## Architecture

```
connector → canonical payload dict
    ↓
detector  → list[PatternResult]     (runs all rules)
    ↓
interpreter → list[Finding]          (one Finding per PatternResult)
    ↓
output    → final JSON dict
```

**Key files:**

| File | Purpose |
|---|---|
| `engine/contracts.py` | Constants: allowed source categories, modes, statuses |
| `engine/models.py` | Dataclasses for all domain entities and engine output types |
| `engine/rules.py` | One `detect_*` function per pattern + `PATTERN_DETECTORS` list |
| `engine/detector.py` | Runs all detectors, returns non-empty results |
| `engine/interpreter.py` | Converts PatternResult → Finding (fallback, no LLM) |
| `engine/output.py` | Assembles final JSON-serializable output |
| `connectors/scenario_connector.py` | Loads a scenario JSON file |
| `connectors/manual_connector.py` | Accepts a Python dict, does light validation |

## Canonical payload shape

```json
{
  "source": { "category": "work_tracking", "mode": "scenario", "product": "manual" },
  "tasks": [
    {
      "id": "T-001",
      "title": "...",
      "status": "open",
      "priority": "high",
      "owner": null,
      "team": null,
      "service": "payments",
      "done_criteria": null,
      "success_metric": null,
      "age_days": 12,
      "in_report": true,
      "labels": ["backend"],
      "history": [
        { "event": "owner_change", "from": "alice", "to": null, "days_ago": 5 }
      ]
    }
  ],
  "pull_requests": [
    {
      "id": "PR-001", "title": "...", "author": "bob",
      "reviewers": [], "status": "open",
      "linked_task_id": "T-001", "age_days": 3
    }
  ],
  "services": [
    { "id": "payments", "name": "Payment Service", "owner_team": null, "criticality": "p0" }
  ]
}
```

## Patterns detected (v1)

| Pattern | What it detects |
|---|---|
| `orphan_work` | Tasks with no owner/team, services with no owner_team, PRs with no reviewers, frequent ownership changes |
| `undefined_outcome` | Active tasks missing `done_criteria` or `success_metric` |
| `priority_translation_failure` | No priority set, urgency/priority mismatch, wide priority spread within a service |
| `untracked_work_dies` | Tasks excluded from reports, stale tasks with no service or metric |
| `circulating_work` | Repeated status changes without completion, status bouncing, old tasks still moving |

## How to run

```bash
# Setup (first time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run against a scenario
python main.py --scenario scenarios/orphan_work_strong.json
python main.py --scenario scenarios/undefined_outcome_strong.json
python main.py --scenario scenarios/mixed_case.json

# Run against your own input file
python main.py --input path/to/your_payload.json

# Run tests
python -m pytest tests/ -v
```

## Adding a new pattern

1. Write a `detect_<pattern_name>(payload: dict) -> PatternResult | None` function in `engine/rules.py`
2. Append it to `PATTERN_DETECTORS`
3. Add a corresponding `_<pattern_name>` function in `engine/interpreter.py`
4. Register it in the `interpreters` dict inside `interpret()`
5. Add a scenario file and tests

No other changes required.

## Out of scope

- No UI
- No database
- No real Jira/GitHub integrations
- No LLM integration
- No plugin system
- No web server
- No generic rule engine or DSL
