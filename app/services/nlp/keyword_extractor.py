import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from app.core.logger import get_logger

__all__ = ["ContrastiveKeywordExtractor"]

logger = get_logger(__name__)


class ContrastiveKeywordExtractor:
    """Extract terms disproportionately common in negative reviews compared to
    positive ones, rather than just frequent within negative reviews alone.

    Plain TF-IDF over negative texts only tends to surface domain-generic
    words (app name, "app", "learning", etc.) that are just as common in
    positive reviews and therefore carry no signal about what's actually
    wrong. Comparing negative vs. positive frequency filters those out
    automatically, without hardcoding a stop-word list per app.
    """

    def __init__(self, top_n: int = 10, min_df: int = 2) -> None:
        self._top_n = top_n
        self._min_df = min_df

    def extract(
        self, negative_texts: list[str], positive_texts: list[str]
    ) -> list[str]:
        if len(negative_texts) < 2:
            return []

        if not positive_texts:
            logger.warning(
                "No positive texts available; falling back to raw negative frequency."
            )
            return self._extract_fallback(negative_texts)

        vectorizer = CountVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            min_df=self._min_df,
        )

        all_texts = negative_texts + positive_texts
        try:
            matrix = vectorizer.fit_transform(all_texts)
        except ValueError:
            logger.warning("Vocabulary empty after min_df filtering; falling back.")
            return self._extract_fallback(negative_texts)

        terms = vectorizer.get_feature_names_out()

        neg_counts = matrix[: len(negative_texts)].sum(axis=0).A1
        pos_counts = matrix[len(negative_texts) :].sum(axis=0).A1

        neg_total = neg_counts.sum() or 1
        pos_total = pos_counts.sum() or 1

        neg_freq = neg_counts / neg_total
        pos_freq = pos_counts / pos_total

        scores = np.log((neg_freq + 1e-6) / (pos_freq + 1e-6))

        term_scores = sorted(zip(terms, scores, strict=True), key=lambda x: -x[1])
        return [term for term, score in term_scores[: self._top_n] if score > 0]

    def _extract_fallback(self, negative_texts: list[str]) -> list[str]:
        """Plain frequency extraction when there's no positive corpus to contrast against."""
        vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform(negative_texts)
        mean_scores = matrix.mean(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        term_scores = sorted(zip(terms, mean_scores, strict=True), key=lambda x: -x[1])
        return [term for term, _ in term_scores[: self._top_n]]
