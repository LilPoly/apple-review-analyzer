from app.core.config.base import BaseConfig

__all__ = ["BertConfig"]


class BertConfig(BaseConfig):
    MODEL_PATH: str = "ml/artifacts/bert/bert-sentiment-v1"
    MAX_LENGTH: int = 128

    model_config = BaseConfig.model_config | {"env_prefix": "BERT_"}
