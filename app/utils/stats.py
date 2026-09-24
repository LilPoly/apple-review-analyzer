import pandas as pd

__all__ = ["calculate_average_rating", "calculate_rating_distribution"]


def calculate_average_rating(ratings: list[int]) -> float:
    if not ratings:
        return 0.0
    series = pd.Series(ratings)
    return round(series.mean(), 2)


def calculate_rating_distribution(ratings: list[int]) -> dict[int, float]:
    """Return the percentage share of each rating value (1-5)."""
    if not ratings:
        return {star: 0.0 for star in range(1, 6)}

    series = pd.Series(ratings)
    percentages = series.value_counts(normalize=True).mul(100).round(2)
    return {star: float(percentages.get(star, 0.0)) for star in range(1, 6)}
