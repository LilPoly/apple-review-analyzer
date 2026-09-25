import uuid
from datetime import datetime, timezone

import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.core.constants import METHODS, TEMPLATE_DIR
from app.core.logger import get_logger
from app.db.unit_of_work import UnitOfWork
from app.services.insights.rule_based_generator import RuleBasedInsightsGenerator
from app.services.report.chart_utils import fig_to_base64_uri

__all__ = ["PdfReportService"]

logger = get_logger(__name__)


class PdfReportService:
    def __init__(
        self,
        uow: UnitOfWork,
        insights_generator: RuleBasedInsightsGenerator,
    ) -> None:
        self._uow = uow
        self._insights_generator = insights_generator
        self._env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
        )

    def generate(self, job_id: uuid.UUID) -> bytes:
        with self._uow as uow:
            job = uow.jobs.get(job_id)
            if job is None:
                raise ValueError(f"Job '{job_id}' not found")

            reviews = uow.reviews.get_by_job_id(job_id)
            if not reviews:
                raise ValueError(f"No reviews found for job_id='{job_id}'")

            review_text_by_id = {str(r.id): r.text for r in reviews}

            ratings = [r.rating for r in reviews]
            avg_rating = round(sum(ratings) / len(ratings), 2)
            rating_distribution = self._rating_distribution(ratings)

            method_sections = []
            for method in METHODS:
                result = uow.results.get_by_job_and_method(job_id, method)
                if result is None:
                    continue

                sentiment_distribution = result.metrics["sentiment_distribution"]
                negative_keywords = result.metrics["negative_keywords"]

                negative_texts = [
                    review_text_by_id[pred["review_id"]]
                    for pred in result.metrics["predictions"]
                    if pred["label"] == "negative"
                    and pred["review_id"] in review_text_by_id
                ]

                insights = self._insights_generator.generate(
                    negative_keywords, negative_texts
                )

                method_sections.append(
                    {
                        "method": method,
                        "sentiment_chart": self._sentiment_chart(
                            sentiment_distribution
                        ),
                        "negative_keywords": negative_keywords,
                        "insights": insights,
                        "execution_time": result.execution_time_seconds,
                    }
                )

            if not method_sections:
                raise ValueError(
                    f"No analysis results found for job_id='{job_id}'. "
                    "Call /jobs/{job_id}/insights first."
                )

        context = {
            "app_id": job.app_id,
            "country": job.country,
            "job_id": str(job_id),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "total_reviews": len(reviews),
            "avg_rating": avg_rating,
            "rating_chart": self._rating_chart(rating_distribution),
            "method_sections": method_sections,
        }

        html_string = self._env.get_template("report.html").render(**context)
        return HTML(string=html_string, base_url=".").write_pdf()

    @staticmethod
    def _rating_distribution(ratings: list[int]) -> dict[int, float]:
        total = len(ratings)
        counts = {star: 0 for star in range(1, 6)}
        for rating in ratings:
            counts[rating] = counts.get(rating, 0) + 1
        return {star: round((count / total) * 100, 2) for star, count in counts.items()}

    @staticmethod
    def _rating_chart(distribution: dict[int, float]) -> str:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(
            [str(s) for s in distribution], list(distribution.values()), color="#4C72B0"
        )
        ax.set_xlabel("Stars")
        ax.set_ylabel("% of reviews")
        ax.set_title("Rating distribution")
        return fig_to_base64_uri(fig)

    @staticmethod
    def _sentiment_chart(distribution: dict[str, float]) -> str:
        colors = {"positive": "#55A868", "neutral": "#C4B454", "negative": "#C44E52"}
        labels = list(distribution.keys())
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(
            labels,
            list(distribution.values()),
            color=[colors.get(label, "#4C72B0") for label in labels],
        )
        ax.set_ylabel("% of reviews")
        ax.set_title("Sentiment distribution")
        return fig_to_base64_uri(fig)
