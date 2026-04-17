from __future__ import annotations

from engine.models import PatternResult
from engine.rules import PATTERN_DETECTORS


def apply_suppression(results: list[PatternResult]) -> list[PatternResult]:
    # Suppress circulating_work when orphan_work (HIGH) shares at least one entity
    orphan_high_ids: set[str] = set()
    for r in results:
        if r.pattern == "orphan_work" and r.severity == "high":
            orphan_high_ids.update(r.matched_ids)

    if not orphan_high_ids:
        return results

    return [
        r for r in results
        if not (
            r.pattern == "circulating_work"
            and bool(set(r.matched_ids) & orphan_high_ids)
        )
    ]


def detect_patterns(payload: dict) -> list[PatternResult]:
    """Run all registered detectors and return non-empty results after suppression."""
    raw: list[PatternResult] = []
    for detect in PATTERN_DETECTORS:
        result = detect(payload)
        if result is not None:
            raw.append(result)
    return apply_suppression(raw)
