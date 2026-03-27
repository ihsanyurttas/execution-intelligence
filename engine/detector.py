from __future__ import annotations

from engine.models import PatternResult
from engine.rules import PATTERN_DETECTORS


def detect_patterns(payload: dict) -> list[PatternResult]:
    """Run all registered detectors and return non-empty results."""
    results = []
    for detect in PATTERN_DETECTORS:
        result = detect(payload)
        if result is not None:
            results.append(result)
    return results
