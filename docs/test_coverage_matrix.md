# Test Coverage Matrix

| Pattern                    | Positive | Negative | Exclusion | Scenario | Mixed |
|----------------------------|----------|----------|-----------|----------|-------|
| orphan_work                | yes      | yes      | yes       | yes      | yes   |
| undefined_outcome          | yes      | yes      | yes       | yes      | yes   |
| priority_translation_failure | yes    | yes      | **no**    | **no**   | yes   |
| untracked_work_dies        | yes      | yes      | yes       | **no**   | yes   |
| circulating_work           | yes      | yes      | yes       | **no**   | yes   |

## Coverage Notes

**Positive** — at least one test that expects the pattern to fire
**Negative** — at least one test that expects no result (valid data, no signal)
**Exclusion** — at least one test that verifies done/inactive tasks are skipped
**Scenario** — dedicated `scenarios/*.json` file with end-to-end test
**Mixed** — covered by `mixed_case.json` end-to-end test

## Gaps

| Gap | What's missing |
|-----|----------------|
| `priority_translation_failure` — Exclusion | No test verifying `done` tasks are excluded from priority checks |
| `priority_translation_failure` — Scenario | No dedicated scenario JSON + `TestPriorityTranslationFailureScenario` class |
| `untracked_work_dies` — Scenario | No dedicated scenario JSON + `TestUntrackedWorkDiesScenario` class |
| `circulating_work` — Scenario | No dedicated scenario JSON + `TestCirculatingWorkScenario` class |
