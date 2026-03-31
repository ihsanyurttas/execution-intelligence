# Project Context

## What this does
Deterministic pattern detection engine. Receives a JSON payload (tasks, PRs, services), runs 5 rules, returns structured findings with evidence + specific improvement actions. No LLM. No database.

## Open this first
```
engine/rules.py        ← where patterns are detected
engine/interpreter.py  ← where findings are generated (text + actions)
engine/models.py       ← PatternResult, Finding, ImprovementTask
```

## Run in 10 seconds
```bash
source .venv/bin/activate
python -m pytest tests/ -q                                    # 44 tests, ~0.05s
python main.py --scenario scenarios/orphan_work_strong.json   # CLI run
open http://localhost:30080                                    # UI (already running in k8s)
```

## Pipeline (one line per file)
```
connectors/scenario_connector.py  →  load JSON
engine/detector.py                →  run all PATTERN_DETECTORS
engine/interpreter.py             →  PatternResult → Finding
engine/output.py                  →  assemble final JSON
app.py                            →  Flask: POST /analyze calls the above
```

## Adding a pattern (4 steps, nothing else needed)
1. `engine/rules.py` — write `detect_X(payload)`, append to `PATTERN_DETECTORS`, populate `context` dict
2. `engine/interpreter.py` — write `_X(result)`, register in dispatch map
3. `tests/test_rules.py` — unit tests
4. `scenarios/X_strong.json` + `tests/test_scenarios.py` — integration test

## context dict (architectural decision — read before touching)
`PatternResult.context` carries structured entity data from rule → interpreter.
**Why not parse signals?** Fragile. Signals are human-readable strings, not a contract.
**Why not pass full payload?** Interpreter would re-detect. Separation breaks.
**Known risk:** context keys are undocumented strings. If a key is missing, interpreter silently gets `[]`. Add keys explicitly in the rule and consume them by name in the interpreter.
Current keys in use:
```
orphan_work:  tasks_no_owner, services_no_owner_team, tasks_churning, prs_no_reviewer
```
The other 4 rules do NOT yet populate context → their interpreters still produce generic output.

## Severity (engine-level, not UI-derived)
| Pattern | Severity |
|---------|---------|
| orphan_work | high |
| undefined_outcome | high |
| untracked_work_dies | high |
| priority_translation_failure | medium |
| circulating_work | low |

## Kubernetes (Docker Desktop)
```bash
docker build -t exec-intel:latest .
kubectl rollout restart deployment/exec-intel -n exec-intel
kubectl rollout status deployment/exec-intel -n exec-intel
```
Namespace: `exec-intel` · NodePort: 30080 · Image pull policy: Never (local only)
