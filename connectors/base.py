from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def source_descriptor(self) -> dict:
        """Return metadata describing the source (mode, product, etc.)."""

    @abstractmethod
    def load(self) -> dict:
        """Return the canonical payload dict ready for the engine."""
