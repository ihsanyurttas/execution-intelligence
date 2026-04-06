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

Your task is to convert a natural language description into valid, clean, and directly runnable JSON.

STRICT REQUIREMENTS:
- Output ONLY valid JSON
- Do NOT include explanations, comments, or markdown
- Use ONLY standard ASCII double quotes (") — never use smart quotes
- Ensure the JSON is fully parseable by Python's json module
- Do NOT include trailing commas
- Do NOT include extra text before or after JSON
- Keep it small and realistic

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
Each task MUST include:
- id (T-001, T-002, ...)
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
- history (array of objects)

3. pull_requests:
- id (PR-001, ...)
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

SCENARIO MODELING RULE (CRITICAL):
- Model the situation as described, not as an idealized or expanded version of it
- Do NOT invent extra tasks, pull requests, or services unless they are clearly implied
- Prefer fewer, more realistic entities over artificially complete scenarios
- If the situation mainly describes a single problematic task, represent that task accurately instead of generating synthetic follow-up work

FINAL VALIDATION (VERY IMPORTANT):
Before returning the response:
- ensure all quotes are standard ASCII double quotes (")
- ensure there are no smart quotes or special characters
- ensure there are no trailing commas
- ensure the JSON is syntactically valid and complete
- if invalid, regenerate until valid

---

Now convert this situation:

[PASTE YOUR TEAM SITUATION HERE]
```
Example Situation : "We have a task open for 10 months with 4 ownership changes and no progress."

---


### Then run:

```bash
python main.py --input path/to/generated.json
```

---

### Troubleshooting JSON Issues

If your JSON fails to parse, it is usually due to quote characters introduced by editors or AI tools.

#### Validate JSON

```bash
python -m json.tool path/to/generated.json
```

If this prints formatted JSON, your file is valid.

---

#### Fix smart quotes (common issue)

Some tools replace standard quotes (") with smart quotes (“ ”), which breaks JSON.

##### macOS

```bash
sed -i '' 's/“/"/g; s/”/"/g' path/to/generated.json
```

##### Linux

```bash
sed -i 's/“/"/g; s/”/"/g' path/to/generated.json
```

---

#### Tip

If you see errors like:

```
Expecting property name enclosed in double quotes
```

It almost always means your file contains invalid quote characters.


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