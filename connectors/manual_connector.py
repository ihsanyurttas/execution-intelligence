from connectors.base import BaseConnector
from engine.contracts import SOURCE_CATEGORIES, SOURCE_MODES


class ManualConnector(BaseConnector):
    """
    Accepts a Python dict and returns it as the canonical payload.
    Does light validation only — no schema enforcement beyond the essentials.
    """

    def __init__(self, payload: dict):
        self._payload = payload

    def source_descriptor(self) -> dict:
        return {"mode": "user_provided"}

    def load(self) -> dict:
        self._validate(self._payload)
        return self._payload

    def _validate(self, payload: dict) -> None:
        if "tasks" not in payload:
            raise ValueError("Payload must contain a 'tasks' key")
        if not isinstance(payload["tasks"], list):
            raise ValueError("'tasks' must be a list")

        source = payload.get("source", {})
        category = source.get("category")
        if category and category not in SOURCE_CATEGORIES:
            raise ValueError(
                f"Unknown source category '{category}'. "
                f"Allowed: {SOURCE_CATEGORIES}"
            )
        mode = source.get("mode")
        if mode and mode not in SOURCE_MODES:
            raise ValueError(
                f"Unknown source mode '{mode}'. "
                f"Allowed: {SOURCE_MODES}"
            )
