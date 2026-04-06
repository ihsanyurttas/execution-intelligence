# Execution Intelligence Engine

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
  "pattern": "orphan_work",
  "evidence": [
    "Task T-001 has no owner",
    "Service payments has no owner_team"
  ],
  "interpretation": "Work exists without clear ownership, leading to stalled execution",
  "suggested_improvements": [
    "Assign a single accountable owner per task",
    "Define ownership for each service"
  ]
}
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

The system is designed to be extensible — new patterns can be added as additional failure modes are identified.

---

## Why This Matters

Infrastructure and metrics show *what* is happening.

This system explains *why*.

It shifts focus from:
- system health → execution health
- resource tuning → coordination and ownership

---

## How to Run

```bash
python main.py --scenario scenarios/mixed_case.json
```

---

## Status

This is an early prototype focused on:
- deterministic pattern detection
- structured interpretation
- reproducible scenarios

Future directions:
- real connectors (Jira, GitHub)
- LLM-assisted interpretation
- prioritization and scoring