import json

from connectors.base import BaseConnector


class ScenarioConnector(BaseConnector):
    """Loads a pre-built scenario JSON file as the canonical payload."""

    def __init__(self, path: str):
        self._path = path

    def source_descriptor(self) -> dict:
        return {"mode": "scenario", "path": self._path}

    def load(self) -> dict:
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)
