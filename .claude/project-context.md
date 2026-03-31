# Project Context

## Purpose
Execution Intelligence Engine (EIE) — a deterministic, LLM-free pattern detection system that analyzes engineering work data (tasks, PRs, services) and surfaces execution problems with specific, actionable improvements.

The system answers three questions:
1. What is wrong? (pattern detection)
2. Why is it happening? (evidence-driven interpretation)
3. What should I do next? (entity-specific improvement actions)

## Stack
- Python 3.9+ (no frameworks in engine layer — pure dict operations)
- Flask 3.x (web UI + API server — `app.py`)
- pytest 8.x (test runner)
- Docker + Kubernetes (Docker Desktop, namespace `exec-intel`, NodePort 30080)

## Key Entry Points
| File | Purpose |
|------|---------|
| `app.py` | Flask server: `GET /`, `POST /analyze`, `GET /scenarios`, `GET /scenarios/<name>` |
| `main.py` | CLI: `python main.py --scenario <file>` or `--input <file>` |
| `engine/rules.py` | 5 detection functions + `PATTERN_DETECTORS` registry |
| `engine/interpreter.py` | Converts `PatternResult` → `Finding` with entity-specific text |

## Pipeline
```
Connector → canonical dict → Detector → [PatternResult] → Interpreter → [Finding] → Output JSON
```

## Core Models (engine/models.py)
- `PatternResult`: pattern, matched_ids, signals, severity (high|medium|low), context (dict)
- `Finding`: pattern, severity, issue, evidence, interpretation, suggested_improvements
- `ImprovementTask`: action, owner_hint, urgency (immediate|short_term|ongoing)

## Canonical Payload Shape
```json
{
  "source": {"category": "work_tracking", "mode": "scenario", "product": "manual"},
  "tasks": [{ "id", "title", "status", "priority", "owner", "team", "service",
              "done_criteria", "success_metric", "age_days", "in_report",
              "labels": [], "history": [{"event", "from", "to", "days_ago"}] }],
  "pull_requests": [{ "id", "title", "author", "reviewers", "status", "linked_task_id", "age_days" }],
  "services": [{ "id", "name", "owner_team", "criticality" }]
}
```

## Commands
```bash
# Setup (once)
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Test
source .venv/bin/activate && python -m pytest tests/ -v

# Run single test
python -m pytest tests/test_rules.py::TestOrphanWork::test_task_with_no_owner_and_no_team_is_detected -v

# Run CLI
python main.py --scenario scenarios/orphan_work_strong.json

# Run Flask locally
python app.py

# Build + deploy to Docker Desktop Kubernetes
docker build -t exec-intel:latest .
kubectl apply -f k8s/
kubectl rollout restart deployment/exec-intel -n exec-intel

# UI
open http://localhost:30080
```

## Detection Rules & Severities
| Pattern | Severity | Key Signals |
|---------|----------|------------|
| orphan_work | high | no owner+team, service with no owner_team, >= 2 ownership changes, open PR no reviewer |
| undefined_outcome | high | missing done_criteria or success_metric on active task |
| priority_translation_failure | medium | urgency label vs low priority mismatch, >= 3 distinct priorities per service |
| untracked_work_dies | high | in_report=false, no metric + no service + age >= 7 days |
| circulating_work | low | >= 3 status changes, status bounce, age >= 14 + >= 2 status changes |

## Extending: Adding a New Pattern
1. Add detector function in `engine/rules.py`, append to `PATTERN_DETECTORS`
2. Populate `context` dict with structured entity data for the interpreter
3. Add interpreter in `engine/interpreter.py`, register in dispatch map
4. Add scenario JSON in `scenarios/`, tests in `tests/test_rules.py` and `tests/test_scenarios.py`

## Constraints
- Always use `.venv` for pip, never install globally
- No LLM calls anywhere in the engine — all output is deterministic
- Do not change canonical payload shape without updating contracts.py + all scenarios
- `context` dict in PatternResult is the bridge between rules and interpreter — use it to pass entity IDs, not string parsing
