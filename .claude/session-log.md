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

## 2026-04-01T16:43:06
- session_id: fed99df8-4b72-4bb4-b600-ed1dafcb4d69
- reason: prompt_input_exit
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/fed99df8-4b72-4bb4-b600-ed1dafcb4d69.jsonl

## 2026-04-01 (end-session, no code changes)

No code written this session. Session opened and ended immediately via /end-session.
State is unchanged from last session. `session-summary.md` and `next-steps.md` remain current.
Next action: start Step 1 — rewrite `detect_undefined_outcome` in `engine/rules.py` to populate context, then rewrite `_undefined_outcome` in `engine/interpreter.py`.

## 2026-04-01T17:01:36
- session_id: 6b903a8b-08c1-4603-b7f9-1db1a17d5cb6
- reason: prompt_input_exit
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/6b903a8b-08c1-4603-b7f9-1db1a17d5cb6.jsonl

## 2026-04-01T17:30:58
- session_id: 6b903a8b-08c1-4603-b7f9-1db1a17d5cb6
- reason: prompt_input_exit
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/6b903a8b-08c1-4603-b7f9-1db1a17d5cb6.jsonl

## 2026-04-01T17:34:01
- session_id: 6b903a8b-08c1-4603-b7f9-1db1a17d5cb6
- reason: prompt_input_exit
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/6b903a8b-08c1-4603-b7f9-1db1a17d5cb6.jsonl

## 2026-04-01T17:39:18
- session_id: c516646b-96ba-43c5-b107-91414bd8a1ce
- reason: other
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/c516646b-96ba-43c5-b107-91414bd8a1ce.jsonl

## 2026-04-01T17:41:21
- session_id: 9b0bbc6e-0d11-49ee-afe1-665445ad0dc7
- reason: other
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/9b0bbc6e-0d11-49ee-afe1-665445ad0dc7.jsonl

## 2026-04-01 (repo analysis + MCP setup)

No code changes. Session focused on repo health analysis and tooling setup.

**Git analysis results:**
- `templates/index.html`: most unstable (3 commits, +835/-106 lines)
- Engine trinity (`interpreter.py`, `rules.py`, `models.py`): always co-change — treat as one unit
- Risk cluster: 2026-03-28, 4 commits in 84 min

**MCP server setup:**
- Playwright MCP added and confirmed connected (`npx @playwright/mcp@latest`)
- Git MCP added but failed to connect (`npx @modelcontextprotocol/server-git`) — needs investigation
- MCP tools only usable after session restart — Playwright validation of localhost:30080 deferred to next session

**Next session must:**
1. Start fresh so Playwright MCP tools are available
2. Validate localhost:30080 main flow with Playwright
3. Then proceed to Step 1 of next-steps.md (rewrite `undefined_outcome`)

## 2026-04-01T17:45:41
- session_id: d110c43b-3f0c-4aa5-9771-52d544eda865
- reason: prompt_input_exit
- transcript_path: /Users/ihsanyurttas/.claude/projects/-Users-ihsanyurttas-Desktop-mydrive-git-execution-intelligence-engine/d110c43b-3f0c-4aa5-9771-52d544eda865.jsonl

## 2026-04-02 (Playwright UI test — partial)

No code changes. Tested `localhost:30080` via Playwright MCP.

**Results:**
- Page loads, title correct, all 8 scenario buttons present ✓
- `favicon.ico` 404 — harmless ✓
- Browser context crashed after clicking `orphan work ★` — Analyze flow not validated
- Root cause: tool-schema fetches between Playwright calls gave the headless browser time to close

**Next session:** run Playwright calls in rapid sequence (no gaps) to complete flow test, then move to Step 1 (`undefined_outcome` interpreter rewrite).
