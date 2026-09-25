from app.core.constants import DEFAULT_INSIGHT, KEYWORD_TO_INSIGHT
from app.services.insights.base import InsightsGenerator

__all__ = ["RuleBasedInsightsGenerator"]


class RuleBasedInsightsGenerator(InsightsGenerator):
    @property
    def generator_type(self) -> str:
        return "rule_based"

    def generate(
        self, negative_keywords: list[str], negative_texts: list[str]
    ) -> list[str]:
        if not negative_keywords:
            return [
                "No significant negative patterns detected in this batch of reviews."
            ]

        insights = []
        matched_keywords = set()

        for keyword in negative_keywords:
            for trigger, insight in KEYWORD_TO_INSIGHT.items():
                if trigger in keyword.lower() and trigger not in matched_keywords:
                    insights.append(insight)
                    matched_keywords.add(trigger)

        if not insights:
            insights.append(DEFAULT_INSIGHT)

        return insights
