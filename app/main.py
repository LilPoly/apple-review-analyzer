from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config.settings import settings
from app.core.logger import get_logger
from app.services.nlp.bert_analyzer import BertAnalyzer

__all__ = ["app"]

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading BERT model into memory...")
    app.state.bert_analyzer = BertAnalyzer(
        model_path=str(settings.bert.MODEL_PATH),
        max_length=settings.bert.MAX_LENGTH,
    )
    logger.info("BERT model loaded successfully")

    yield

    logger.info("Shutting down, releasing resources...")


app = FastAPI(title="Apple Store Review Analyzer", lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
