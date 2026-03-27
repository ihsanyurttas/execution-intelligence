from __future__ import annotations
import dataclasses
from datetime import datetime, timezone

from engine.models import Finding


def assemble(findings: list[Finding], payload: dict) -> dict:
    """Assemble the final JSON-serializable output dict."""
    source = payload.get("source", {})
    tasks = payload.get("tasks", [])
    prs = payload.get("pull_requests", [])
    services = payload.get("services", [])

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_summary": {
            "source": source,
            "task_count": len(tasks),
            "pr_count": len(prs),
            "service_count": len(services),
        },
        "findings": [dataclasses.asdict(f) for f in findings],
    }
