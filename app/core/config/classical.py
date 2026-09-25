from app.core.config.base import BaseConfig

__all__ = ["ClassicalConfig"]


class ClassicalConfig(BaseConfig):
    MODEL_PATH: str = "ml/artifacts/classical/tfidf_logreg_v1.joblib"
    BASELINE_METRICS_PATH: str = "ml/artifacts/baseline_metrics.json"

    model_config = BaseConfig.model_config | {"env_prefix": "CLASSICAL_"}
