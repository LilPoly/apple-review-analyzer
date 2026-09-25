import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

__all__ = ["ChartService"]


class ChartService:
    def rating_distribution_chart(self, distribution: dict[int, float]) -> io.BytesIO:
        stars = sorted(distribution.keys())
        percentages = [distribution[star] for star in stars]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar([f"{s}★" for s in stars], percentages, color="#4C72B0")
        ax.set_ylabel("Percentage of reviews (%)")
        ax.set_title("Rating Distribution")
        ax.bar_label(bars, fmt="%.1f%%")
        ax.set_ylim(0, max(percentages) * 1.2 if percentages else 100)

        return self._figure_to_bytes(fig)

    def sentiment_distribution_chart(
        self, distribution: dict[str, float], method: str
    ) -> io.BytesIO:
        labels = list(distribution.keys())
        percentages = list(distribution.values())
        colors = {"positive": "#55A868", "neutral": "#CCB974", "negative": "#C44E52"}
        bar_colors = [colors.get(label, "#4C72B0") for label in labels]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(labels, percentages, color=bar_colors)
        ax.set_ylabel("Percentage of reviews (%)")
        ax.set_title(f"Sentiment Distribution ({method})")
        ax.bar_label(bars, fmt="%.1f%%")
        ax.set_ylim(0, max(percentages) * 1.2 if percentages else 100)

        return self._figure_to_bytes(fig)

    def model_comparison_chart(
        self, macro_f1_by_method: dict[str, float]
    ) -> io.BytesIO:
        methods = list(macro_f1_by_method.keys())
        scores = list(macro_f1_by_method.values())

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(methods, scores, color="#8172B2")
        ax.set_ylabel("Macro F1 Score")
        ax.set_title("Model Comparison — Macro F1 on Test Set")
        ax.bar_label(bars, fmt="%.2f")
        ax.set_ylim(0, 1.0)

        return self._figure_to_bytes(fig)

    def _figure_to_bytes(self, fig) -> io.BytesIO:
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)
        return buffer
