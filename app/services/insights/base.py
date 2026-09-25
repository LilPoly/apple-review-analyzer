from abc import ABC, abstractmethod

__all__ = ["InsightsGenerator"]


class InsightsGenerator(ABC):
    @property
    @abstractmethod
    def generator_type(self) -> str: ...

    @abstractmethod
    def generate(
        self, negative_keywords: list[str], negative_texts: list[str]
    ) -> list[str]:
        """Generate human-readable actionable insights from negative review data."""
        ...
