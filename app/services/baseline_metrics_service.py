import json
from pathlib import Path

from app.core.exceptions import BaselineMetricsReadError
from app.schemas.baseline import BaselineMetricsResponse

__all__ = ["BaselineMetricsService"]


class BaselineMetricsService:
    def __init__(self, report_path: Path) -> None:
        self._report_path = Path(report_path)

    def get_metrics(self) -> BaselineMetricsResponse:
        if not self._report_path.exists():
            raise BaselineMetricsReadError(
                f"Baseline metrics report not found at {self._report_path}. "
                "Run 'python -m ml.generate_baseline_report' first."
            )

        with open(self._report_path, encoding="utf-8") as f:
            data = json.load(f)

        return BaselineMetricsResponse.model_validate(data)
