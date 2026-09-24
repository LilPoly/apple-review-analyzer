from app.core.constants import MIN_MEANINGFUL_WORDS, MULTIPLE_SPACES, URL_PATTERN

__all__ = ["clean_text", "is_meaningful_text"]


def clean_text(text: str) -> str:
    """Normalize raw review text before feeding it into NLP pipelines."""
    text = URL_PATTERN.sub("", text)
    text = MULTIPLE_SPACES.sub(" ", text)
    return text.strip()


def is_meaningful_text(text: str) -> bool:
    """Filter out reviews that are too short to carry useful sentiment signal."""
    return len(text.split()) >= MIN_MEANINGFUL_WORDS
