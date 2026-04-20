import logging

from fastapi import FastAPI
from app.api.routes.ingest import router as ingest_router
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.api.routes.chat import router as chat_router

setup_logging()
logger = logging.getLogger(__name__)

app=FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="电商智能客服 Agent API"
)
app.include_router(ingest_router)
app.include_router(chat_router)

logger.info(
    "FastAPI app initialized | app_name=%s | version=%s | debug=%s",
    settings.app_name,
    settings.app_version,
    settings.debug,
)

@app.get("/health")
def health():
    return {"status": "ok"}