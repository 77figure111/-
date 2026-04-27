import logging
import os
import sys
from fastapi import FastAPI
from app.api.routes.ingest import router as ingest_router
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.api.routes.chat import router as chat_router
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#加日志初始化和启动日志
setup_logging()
#获取当前模块的专属日志器，方便定位日志来自哪个文件
logger = logging.getLogger(__name__)

app=FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="电商智能客服 Agent API"
)
app.include_router(ingest_router)
app.include_router(chat_router)
#用 logger 打印一条 INFO 级别的日志，把 FastAPI 启动成功的信息（服务名、版本、是否调试模式）输出到控制台。
logger.info(
    # %s = 占位符
    "FastAPI app initialized | app_name=%s | version=%s | debug=%s",
    settings.app_name,
    settings.app_version,
    settings.debug,
)
@app.get("/")
def root():
    return {
        "message": "ecom-agent-api is running",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health():
    logger.info("health check called")
    return {"status": "ok"}