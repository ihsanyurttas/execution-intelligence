# Next Steps

## 1. Apply evidence-driven output to remaining 4 interpreters (Priority 3 continued)

Same pattern as `orphan_work`. For each rule:
- Populate `context` in `engine/rules.py` with entity lists
- Rewrite interpreter in `engine/interpreter.py` to build interpretation from context

### `undefined_outcome`
```python
# context to add in detect_undefined_outcome:
context = {
    "tasks_missing_criteria": ["T-801"],   # missing done_criteria
    "tasks_missing_metric": ["T-801", "T-802"],  # missing success_metric
    "tasks_missing_both": ["T-801"],
}

# interpreter generates:
"T-801 and T-802 are in_progress without defined done criteria or success metrics,
making it impossible to determine completion or measure outcome."

[ ] Define explicit done criteria for T-801
[ ] Define a measurable success metric for T-802
[ ] Block tasks from moving to in_progress without done_criteria defined
```

### `untracked_work_dies`
```python
# context:
context = {
    "tasks_not_in_report": ["T-801", "T-802"],
    "tasks_no_metric_and_old": ["T-802"],
}

# interpreter generates:
"T-801 and T-802 are active but excluded from reporting..."

[ ] Add T-801 to the team's weekly report or dashboard
[ ] Define a tracking metric for T-802
```

### `priority_translation_failure` and `circulating_work`
Same approach — extract entity IDs into context, reference them in actions.

---

## 2. Add dominance/suppression rule

When `orphan_work` fires on a task, suppress `circulating_work` for the same task IDs.
Implement in `engine/detector.py` post-detection step — do not change individual rules.

```python
# sketch in detector.py:
def suppress_dominated(results):
    orphan_ids = set(r.matched_ids for r in results if r.pattern == "orphan_work")
    # filter circulating_work matched_ids that overlap
```

---

## 3. Add integration test classes for `circulating_work` and `priority_translation_failure`

`docs/test_coverage_matrix.md` shows Scenario column as `?` for both.
Add `TestCirculatingWorkScenario` and `TestPriorityTranslationFailureScenario` in `tests/test_scenarios.py`.

---

## 4. Tighten `ManualConnector._validate()`

Add field-level validation: check each task has `id`, `status`, `age_days`.
Return a descriptive error instead of crashing with a KeyError deep in the engine.

---

## 5. Rebuild + redeploy after interpreter rewrites

```bash
docker build -t exec-intel:latest .
kubectl rollout restart deployment/exec-intel -n exec-intel
```
