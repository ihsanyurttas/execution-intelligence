# Next Steps

---

## Step 1 — Rewrite `undefined_outcome` interpreter

**Files to touch (in order):**

**1. `engine/rules.py` — function `detect_undefined_outcome` (~line 114)**

Add context tracking inside the task loop, before `return PatternResult(...)`:

```python
ctx_missing_criteria: list[str] = []
ctx_missing_metric: list[str] = []
ctx_missing_both: list[str] = []

# inside the loop, after computing `missing`:
if "done_criteria" in missing:
    ctx_missing_criteria.append(tid)
if "success_metric" in missing:
    ctx_missing_metric.append(tid)
if len(missing) == 2:
    ctx_missing_both.append(tid)
```

Add to `PatternResult(...)`:
```python
context={
    "tasks_missing_criteria": ctx_missing_criteria,
    "tasks_missing_metric": ctx_missing_metric,
    "tasks_missing_both": ctx_missing_both,
},
```

**2. `engine/interpreter.py` — function `_undefined_outcome` (~line 80)**

Replace the entire function body with context-driven logic:

```python
def _undefined_outcome(result: PatternResult) -> Finding:
    ctx = result.context
    missing_criteria = ctx.get("tasks_missing_criteria", [])
    missing_metric = ctx.get("tasks_missing_metric", [])
    missing_both = ctx.get("tasks_missing_both", [])

    # interpretation
    if missing_both:
        ids = ", ".join(missing_both)
        interp = (
            f"{ids} {'is' if len(missing_both) == 1 else 'are'} in progress "
            "without done criteria or success metrics — "
            "completion and outcome cannot be determined."
        )
    elif missing_criteria:
        ids = ", ".join(missing_criteria)
        interp = f"{ids} lack done criteria — the team cannot agree on when this work is finished."
    else:
        ids = ", ".join(missing_metric)
        interp = f"{ids} lack a success metric — outcome cannot be measured after delivery."

    improvements = []
    for tid in missing_criteria:
        improvements.append(ImprovementTask(
            action=f"Define explicit done criteria for {tid} (e.g. 'error rate below X%' or 'feature accepted by QA')",
            owner_hint="task owner",
            urgency="immediate",
        ))
    for tid in missing_metric:
        improvements.append(ImprovementTask(
            action=f"Define a measurable success metric for {tid}",
            owner_hint="product manager",
            urgency="short_term",
        ))
    improvements.append(ImprovementTask(
        action="Block tasks from moving to in_progress without done_criteria defined — enforce at task creation",
        owner_hint="engineering manager",
        urgency="ongoing",
    ))

    return Finding(
        pattern=result.pattern,
        severity=result.severity,
        issue=f"{len(result.matched_ids)} active task(s) have no done criteria or success metric defined.",
        evidence=result.signals,
        interpretation=interp,
        suggested_improvements=improvements,
    )
```

**Test:**
```bash
source .venv/bin/activate && python -m pytest tests/ -q
python main.py --scenario scenarios/undefined_outcome_strong.json
```

**Done when:**
- 44 tests still pass
- Output for `undefined_outcome` references task IDs by name (not "each active task")
- Actions are deduplicated (one per task, not one generic action)

---

## Step 2 — Rewrite `untracked_work_dies` interpreter

**Files:** `engine/rules.py` (~line 216), `engine/interpreter.py` (~line 169)

Context to add in `detect_untracked_work_dies`:
```python
ctx_not_in_report: list[str] = []    # in_report=False
ctx_no_metric_old: list[str] = []    # no metric + no service + age >= threshold
```

Interpreter actions:
```python
# per task in ctx_not_in_report:
f"Add {tid} to the team's weekly report or dashboard immediately"

# per task in ctx_no_metric_old:
f"Define a tracking metric for {tid} or link it to a service — it has been invisible for X days"
```

---

## Step 3 — Add dominance suppression in `engine/detector.py`

When `orphan_work` fires on a task, do not also report `circulating_work` for the same task.
The task is broken at the ownership level — circulation is a symptom, not a separate problem.

**File:** `engine/detector.py`

```python
def suppress_dominated(results: list[PatternResult]) -> list[PatternResult]:
    orphan_ids = set()
    for r in results:
        if r.pattern == "orphan_work":
            orphan_ids.update(r.matched_ids)

    filtered = []
    for r in results:
        if r.pattern == "circulating_work":
            remaining = [i for i in r.matched_ids if i not in orphan_ids]
            if not remaining:
                continue
            r = PatternResult(r.pattern, remaining, r.signals, r.severity, r.context)
        filtered.append(r)
    return filtered
```

Call it in `detect_patterns()` before returning.

---

## Step 4 — Tighten `ManualConnector._validate()`

**File:** `connectors/manual_connector.py`

Add per-task field check after the existing list check:
```python
required_task_fields = {"id", "status", "age_days"}
for i, task in enumerate(tasks):
    missing = required_task_fields - task.keys()
    if missing:
        raise ValueError(f"Task at index {i} is missing required fields: {missing}")
```

This prevents bare `KeyError` crashes deep in rules.py when the payload is malformed.

---

## Step 5 — Add scenario test classes for `circulating_work` and `priority_translation_failure`

**File:** `tests/test_scenarios.py`

Add `TestCirculatingWorkScenario` (scenario file: `circulating_work_strong.json`) and `TestPriorityTranslationFailureScenario` (scenario file: `priority_translation_failure_strong.json`).
Pattern: same structure as existing `TestOrphanWorkScenario`.
