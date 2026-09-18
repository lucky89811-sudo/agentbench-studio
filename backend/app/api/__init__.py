from fastapi import APIRouter
from app.api.routes_tasks import router as tasks_router
from app.api.routes_configs import router as configs_router
from app.api.routes_runs import router as runs_router
from app.api.routes_comparisons import router as comparisons_router
from app.api.routes_reports import router as reports_router
from app.api.routes_pricing import router as pricing_router

api_router = APIRouter()
api_router.include_router(tasks_router)
api_router.include_router(configs_router)
api_router.include_router(runs_router)
api_router.include_router(comparisons_router)
api_router.include_router(reports_router)
api_router.include_router(pricing_router)
