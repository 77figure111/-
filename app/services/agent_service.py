"""
当前系统唯一正式回答中枢。
负责：
1. 接收用户消息
2. 调用 agent
3. 基于 thread_id 维护短期会话上下文
4. 返回最终文本结果
"""
"""
当前系统唯一正式回答中枢。
负责：
1. 接收用户消息
2. 调用 agent
3. 基于 thread_id 维护短期会话上下文
4. 返回最终文本结果
"""
import logging
import time

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from app.services.agent_tools import (
    search_knowledge_base,
    query_order_status,
    query_logistics_status,
    query_refund_status,
)
#调用 file_history_store 的 get_history 函数，实现「会话消息持久化」和「上下文加载」
from app.services.file_history_store import get_history

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
你是一名购物软件智能客服。

你的工作规则如下：
1. 先判断用户是在问：
   - 订单状态
   - 物流状态
   - 退款状态
   - 或知识库类问题（商品信息、尺码、活动、物流政策、售后政策）

2. 如果用户在问订单/物流/退款，但没有提供订单号：
   - 先礼貌追问订单号
   - 不要乱编，不要直接调用订单工具

3. 如果上一轮你刚刚追问了订单号，而这一轮用户只回复了类似“JD10001”这样的订单号：
   - 请结合对话历史判断这是继续上一轮任务
   - 然后调用正确的工具（订单 / 物流 / 退款）

4. 对于商品信息、尺码、活动、物流政策、售后政策类问题：
   - 优先调用 search_knowledge_base
   - 必须优先依赖工具返回的资料，不要脱离资料乱编

5. 如果知识库工具返回“无相关资料”：
   - 明确说“我目前没有足够依据回答这个问题”

6. 回答风格简洁、礼貌，像电商客服。
"""


class AgentService:
    def __init__(self):
        logger.info("initializing AgentService")

        self.model = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0
        )
        #内存存储（重启服务就丢）
        #file_history_store.py 文件持久化存储（重启不丢）永久保存到 JSON 文件里。
        self.checkpointer = InMemorySaver()

        self.agent = create_agent(
            model=self.model,
            tools=[
                search_knowledge_base,
                query_order_status,
                query_logistics_status,
                query_refund_status,
            ],
            system_prompt=SYSTEM_PROMPT,
            checkpointer=self.checkpointer,
        )

        logger.info("AgentService initialized successfully")

    @staticmethod
    def _short_text(text: str, limit: int = 80) -> str:
        text = text.replace("\n", " ").strip()
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
    #保存用户消息（_save_user_message 方法）
    def _save_user_message(self, thread_id: str, user_input: str) -> None:
        try:
            history = get_history(thread_id)
            history.add_messages([HumanMessage(content=user_input)])
            logger.info("user message persisted | thread_id=%s", thread_id)
        except Exception as e:
            logger.exception(
                "failed to persist user message | thread_id=%s | error=%s",
                thread_id,
                str(e),
            )
    #3. 保存 AI 回复消息（_save_ai_message 方法）
    def _save_ai_message(self, thread_id: str, answer_text: str) -> None:
        try:
            history = get_history(thread_id)
            history.add_messages([AIMessage(content=answer_text)])
            logger.info("assistant message persisted | thread_id=%s", thread_id)
        except Exception as e:
            logger.exception(
                "failed to persist assistant message | thread_id=%s | error=%s",
                thread_id,
                str(e),
            )

    def debug_once(self, user_input: str, thread_id: str):
        logger.info(
            "debug_once called | thread_id=%s | input_preview=%s",
            thread_id,
            self._short_text(user_input),
        )

        t0 = time.perf_counter()
        result = self.agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            {
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )
        cost = time.perf_counter() - t0

        logger.info(
            "debug_once finished | thread_id=%s | elapsed=%.3fs | result_type=%s",
            thread_id,
            cost,
            type(result).__name__,
        )

        print("===== AGENT RAW RESULT =====")
        print(type(result))
        print(result)
        print("===== END RAW RESULT =====")
        return result

    def _extract_final_text(self, result) -> str:
        if result is None:
            logger.warning("_extract_final_text got None result")
            return "抱歉，agent 没有返回结果。"

        if not isinstance(result, dict):
            logger.warning(
                "_extract_final_text got non-dict result | type=%s",
                type(result).__name__,
            )
            return f"返回结果不是字典，而是：{type(result)} -> {result}"

        messages = result.get("messages", [])
        if not messages:
            logger.warning("_extract_final_text found empty messages | result=%s", result)
            return f"agent 返回中没有 messages，原始结果是：{result}"

        last_message = messages[-1]
        content = getattr(last_message, "content", "")

        if isinstance(content, str):
            text = content.strip()
            if text:
                return text

        if isinstance(content, list):
            texts = []
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text")
                    if text:
                        texts.append(str(text))
                    else:
                        texts.append(str(block))
                else:
                    texts.append(str(block))

            final_text = "\n".join([t for t in texts if t]).strip()
            if final_text:
                return final_text

        as_text = str(content).strip()
        if as_text:
            return as_text

        logger.warning("last assistant message has no readable text | last_message=%s", last_message)
        return f"最后一条消息没有可读文本，last_message={last_message}"

    def answer(self, user_input: str, thread_id: str) -> str:
        logger.info(
            "agent answer started | thread_id=%s | input_len=%d | input_preview=%s",
            thread_id,
            len(user_input),
            self._short_text(user_input),
        )

        self._save_user_message(thread_id, user_input)

        try:
            t0 = time.perf_counter()

            result = self.agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": user_input}
                    ]
                },
                {
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
            )

            invoke_cost = time.perf_counter() - t0
            logger.info(
                "agent invoke finished | thread_id=%s | elapsed=%.3fs",
                thread_id,
                invoke_cost,
            )

            t1 = time.perf_counter()
            final_text = self._extract_final_text(result)
            extract_cost = time.perf_counter() - t1

            logger.info(
                "agent answer finished | thread_id=%s | answer_len=%d | extract_elapsed=%.3fs",
                thread_id,
                len(final_text),
                extract_cost,
            )

            self._save_ai_message(thread_id, final_text)
            return final_text

        except Exception as e:
            logger.exception(
                "agent answer failed | thread_id=%s | error=%s",
                thread_id,
                str(e),
            )
            fallback_text = "抱歉，当前客服服务暂时不可用，请稍后重试。"
            self._save_ai_message(thread_id, fallback_text)
            return fallback_text