# Execution Intelligence Engine

A source-agnostic prototype for diagnosing execution failure patterns in engineering teams.

A system that diagnoses how engineering work actually executes — and identifies the hidden patterns that drive missed deadlines, unclear ownership, and wasted effort.

---

## The Problem

Most engineering problems are not visible in metrics.

Teams see symptoms:
- work gets stuck
- priorities shift constantly
- ownership is unclear
- deadlines slip

But these are outcomes — not causes.

The real issues live in how work is executed:
- ownership gaps
- undefined outcomes
- priority translation failures
- coordination breakdowns

These patterns are rarely made explicit.

---

## The Idea

Execution Intelligence Engine analyzes engineering signals (tasks, pull requests, services) and identifies these underlying execution patterns.

Instead of reporting status, it answers:

> Why is this work not progressing?

---

## What It Does

**Input:**
- Tasks
- Pull requests
- Services

**Output:**
- Detected execution patterns
- Evidence for each pattern
- Interpretation of what it means
- Suggested improvement actions

---

## Example Output

```json
{
  "findings": [
    {
      "pattern": "orphan_work",
      "severity": "high",
      "issue": "Multiple work items have no clear owner, team, or accountable service.",
      "evidence": [
        "Task T-301 has no owner and no team",
        "Task T-303 has no owner and no team",
        "Task T-305 has no owner and no team",
        "Service 'integrations' has no owner_team",
        "Service 'catalog' has no owner_team",
        "PR-301 is open with no reviewers assigned"
      ],
      "interpretation": "Work exists without clear ownership at both task and service level.",
      "suggested_improvements": [
        "Assign a single accountable owner per task",
        "Define ownership for each service",
        "Ensure every PR has at least one reviewer"
      ]
    }
  ]
}
```

---

## Try It in 30 Seconds

```bash
git clone https://github.com/ihsanyurttas/execution-intelligence
cd execution-intelligence

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py --scenario scenarios/mixed_case.json
```

This is a deterministic prototype — no external APIs, no dependencies beyond Python.

---

## Generate a Scenario with Any AI Chat

You can use any AI chat (ChatGPT, Claude, etc.) to generate a valid input for this system.

Just copy the prompt below, paste it into your AI chat, and describe your situation.

---

### Prompt

```text
You are generating a JSON payload for an engineering execution analysis system.

Your task is to convert a natural language description of an engineering team situation into valid JSON.

STRICT REQUIREMENTS:
- Output ONLY valid JSON (no explanations)
- Ensure the JSON is complete and directly usable
- Keep it small but meaningful (3–6 tasks max)

TOP-LEVEL STRUCTURE:
{
  "source": {...},
  "tasks": [...],
  "pull_requests": [...],
  "services": [...]
}

RULES:

1. source:
- category = "work_tracking"
- mode = "user_provided"
- product = "manual"

2. tasks:
- id (T-001, ...)
- title
- status (open | in_progress | done | blocked)
- priority (critical | high | medium | low | null)
- owner (string or null)
- team (string or null)
- service (string or null)
- done_criteria (string or null)
- success_metric (string or null)
- age_days (integer)
- in_report (true/false)
- labels (array)
- history (array)

3. pull_requests:
- id
- title
- author
- reviewers (array)
- status (open | merged | closed)
- linked_task_id
- age_days

4. services:
- id
- name
- owner_team (string or null)
- criticality (p0 | p1 | p2)

DEFAULTS (if missing):
- owner = null
- team = null
- service = null
- done_criteria = null
- success_metric = null
- reviewers = []
- labels = []
- history = []
- in_report = false
- priority = null
- criticality = "p1"

Include at least:
- one ownership issue
- one unclear outcome
- one coordination or priority issue

---

Now convert this situation:

[PASTE YOUR TEAM SITUATION HERE]
```

---

### Then run:

```bash
python main.py --input path/to/generated.json
```

---

## Architecture

```
connector → canonical payload
      ↓
detector → patterns
      ↓
interpreter → findings
      ↓
output → structured JSON
```

This is intentionally simple:
- no database
- deterministic logic
- easy to extend

---

## Example Patterns

- orphan_work  
- undefined_outcome  
- priority_translation_failure  
- untracked_work_dies  
- circulating_work  

These are examples of execution failure patterns.

The system is designed to be extensible — new patterns can be added.

---

## Why This Matters

Infrastructure and metrics show *what* is happening.

This system explains *why*.

It shifts focus from:
- system health → execution health
- resource tuning → coordination and ownership

---

## Status

This is an initial prototype focused on deterministic pattern detection.

Future directions:
- real connectors (Jira, GitHub)
- LLM-assisted interpretation
- prioritization and scoring