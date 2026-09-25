from fastapi import APIRouter

from app.api.routers.reviews import router as reviews_router
from app.api.routers.analysis import router as analysis_router
from app.api.routers.analytics import router as analytics_router
from app.api.routers.visualizations import router as visualizations_router
from app.api.routers.reports import router as report_router

__all__ = ["api_router"]

api_router = APIRouter()
api_router.include_router(reviews_router)
api_router.include_router(analysis_router)
api_router.include_router(analytics_router)
api_router.include_router(visualizations_router)
api_router.include_router(report_router)
