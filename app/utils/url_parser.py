from app.core.constants import APP_STORE_URL_PATTERN
from app.core.exceptions import InvalidAppUrlError

__all__ = ["extract_app_id", "extract_country", "parse_app_store_url"]


def parse_app_store_url(url: str) -> tuple[str, str]:
    """Extract (app_id, country) from a full App Store URL.

    Raises:
        InvalidAppUrlError: if the URL does not match the expected App Store format.
    """
    match = APP_STORE_URL_PATTERN.search(url)
    if not match:
        raise InvalidAppUrlError(url)
    return match.group("app_id"), match.group("country").lower()


def extract_app_id(url: str) -> str:
    app_id, _ = parse_app_store_url(url)
    return app_id


def extract_country(url: str, default: str = "us") -> str:
    try:
        _, country = parse_app_store_url(url)
        return country
    except InvalidAppUrlError:
        return default
