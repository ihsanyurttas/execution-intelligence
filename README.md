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
      "interpretation": "Work exists without clear ownership at both task and service level. Responsibility shifts without settling, and review processes are blocked.",
      "suggested_improvements": [
        "Assign a single accountable owner per task",
        "Define ownership for each service",
        "Ensure every PR has at least one reviewer"
      ]
    },
    {
      "pattern": "undefined_outcome",
      "severity": "high",
      "issue": "Active tasks are missing done criteria and success metrics.",
      "evidence": [
        "Tasks lack done_criteria",
        "Tasks lack success_metric"
      ],
      "interpretation": "Work progresses without a clear definition of success, making prioritization and validation unreliable.",
      "suggested_improvements": [
        "Define done criteria before starting work",
        "Attach measurable success metrics to each task"
      ]
    }
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

This is an initial prototype focused on deterministic pattern detection.

Future directions:
- real connectors (Jira, GitHub)
- LLM-assisted interpretation
- prioritization and scoring