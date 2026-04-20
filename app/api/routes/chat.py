#把 AgentService 包成 API。
import logging

from fastapi import APIRouter, HTTPException

from app.services.agent_service import AgentService
from app.api.schemas import ChatRequest, ChatResponse
#请求级日志和异常日志
logger = logging.getLogger(__name__)

router=APIRouter(prefix='/chat',tags=['chat'])
agent_service=AgentService()

def _short_text(text: str, limit: int = 60) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "..."

#@router.post提交数据
@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    logger.info(
        "chat request received | thread_id=%s | message_len=%d | preview=%s",
        req.thread_id,
        len(req.message),
        _short_text(req.message),
    )

    try:
        answer = agent_service.answer(req.message, req.thread_id)
        logger.info(
            "chat request finished | thread_id=%s | answer_len=%d",
            req.thread_id,
            len(answer),
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.exception(
            "chat request failed | thread_id=%s | error=%s",
            req.thread_id,
            str(e),
        )
        raise HTTPException(status_code=500, detail="聊天服务处理失败，请稍后重试。")
"""
真正的异步（必须 answer 是异步）
只有你的 agent_service.answer() 是 async def 才能用：answer = await agent_service.answer(req.message, req.thread_id)
"""