# Session Log — Decisions and Intent

## 2026-03-28

**Decision: context dict on PatternResult**
Added `context: dict` to `PatternResult` so rules can pass structured entity data (task IDs, service IDs) to interpreters without the interpreter re-running detection or parsing signal strings.
Tradeoff accepted: keys are untyped strings. Risk: silent empty list if key missing. Mitigation: document keys in project-context.md, use `.get("key", [])` defensively.

**Decision: severity is engine-level, not UI-derived**
Previous UI derived urgency from improvement urgency list. Problem: all patterns showed HIGH because all had at least one `immediate` improvement. Fix: each rule emits `severity` on `PatternResult`, interpreter passes it to `Finding`, UI reads `f.severity` directly.
Pattern → severity mapping: orphan_work=high, undefined_outcome=high, untracked_work_dies=high, priority_translation_failure=medium, circulating_work=low.

**Decision: remove "missing priority" from priority_translation_failure**
A single task with `null` priority is a data quality gap, not a systemic pattern. The pattern is meaningful only when there is a conflict (urgency label + low priority) or spread (>= 3 distinct priorities in one service).

**Decision: tighten circulating_work age signal**
`age >= 14 AND any history` was too broad — a 15-day-old task with 1 status change and 1 owner change is normal. Changed to `age >= 14 AND >= 2 status changes`.

## 2026-03-31

**Decision: session files should be executable, not descriptive**
First version of `.claude/` files was summary-heavy. Rewritten to be operational: exact file paths, exact functions, exact commands, exact code to copy. A session file that doesn't answer "what file do I open?" is useless.
