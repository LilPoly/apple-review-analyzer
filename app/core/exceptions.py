__all__ = ["AppNotFoundError", "InvalidAppUrlError", "ScraperError"]


class AppNotFoundError(Exception):
    """Raised when no app with the given app_id exists in the App Store."""

    def __init__(self, app_id: str) -> None:
        self.app_id = app_id
        super().__init__(f"App with id '{app_id}' not found in App Store")


class InvalidAppUrlError(Exception):
    """Raised when the provided URL is not a valid App Store app URL."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"Could not extract app_id from URL: '{url}'")


class ScraperError(Exception):
    """Raised for generic failures during review collection (network, parsing, etc.)."""


class BaselineMetricsReadError(Exception):
    """Raised when the baseline metrics report file is missing or invalid."""
