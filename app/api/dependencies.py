from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request

from app.core.config.settings import settings
from app.db.redis import redis_client
from app.db.session import SessionLocal
from app.db.unit_of_work import UnitOfWork
from app.services.baseline_metrics_service import BaselineMetricsService
from app.services.cache_service import CacheService
from app.services.nlp.bert_analyzer import BertAnalyzer
from app.services.nlp.classical_analyzer import ClassicalAnalyzer
from app.services.nlp.keyword_extractor import ContrastiveKeywordExtractor
from app.services.nlp.vader_analyzer import VaderAnalyzer
from app.services.report.pdf_report_service import PdfReportService
from app.services.scraper.apple_rss_scraper import AppleRSSScraper
from app.services.scraper.base import ScraperService
from app.services.scraper.cached_scraper import CachedScraper
from app.services.sentiment_analysis_service import SentimentAnalysisService
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.insights.base import InsightsGenerator
from app.services.insights.rule_based_generator import RuleBasedInsightsGenerator

__all__ = ["get_uow", "get_sentiment_analysis_service"]


def get_uow() -> UnitOfWork:
    return UnitOfWork(SessionLocal)


def get_scraper() -> ScraperService:
    fetcher = AppleRSSScraper()
    cache = CacheService(redis_client)
    return CachedScraper(fetcher=fetcher, cache=cache)


@lru_cache
def get_vader_analyzer() -> VaderAnalyzer:
    return VaderAnalyzer()


@lru_cache
def get_classical_analyzer() -> ClassicalAnalyzer:
    return ClassicalAnalyzer(model_path=str(settings.classical.MODEL_PATH))


def get_bert_analyzer(request: Request) -> BertAnalyzer:
    return request.app.state.bert_analyzer


def get_sentiment_analysis_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    vader: Annotated[VaderAnalyzer, Depends(get_vader_analyzer)],
    classical: Annotated[ClassicalAnalyzer, Depends(get_classical_analyzer)],
    bert: Annotated[BertAnalyzer, Depends(get_bert_analyzer)],
) -> SentimentAnalysisService:
    return SentimentAnalysisService(
        uow=uow,
        analyzers=[vader, classical, bert],
        keyword_extractor=ContrastiveKeywordExtractor(),
    )


def get_baseline_metrics_service() -> BaselineMetricsService:
    return BaselineMetricsService(
        report_path=Path(settings.classical.BASELINE_METRICS_PATH)
    )


def get_anomaly_detection_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> AnomalyDetectionService:
    return AnomalyDetectionService(uow=uow)


def get_insights_generator() -> InsightsGenerator:
    return RuleBasedInsightsGenerator()


def get_pdf_report_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> PdfReportService:
    return PdfReportService(
        uow=uow,
        insights_generator=RuleBasedInsightsGenerator(),
    )
