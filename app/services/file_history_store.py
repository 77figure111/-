#存储会话历史消息存储会话历史消息
"""
#1.初始化：接收 session_id
（对应 agent_service 中的 thread_id）和存储路径，
生成每个会话独立的 JSON 文件
（路径：./chat_history/{session_id}.json）。

#2.add_messages将新消息（用户 / AI 消息）追加到历史消息列表，序列化后写入 JSON 文件（覆盖式写入，保证历史完整）。

#3.messages 属性：从 JSON 文件中读取历史消息，反序列化为 LangChain 的 BaseMessage 对象列表（兼容 LangChain 生态）。

#4.clear：清空指定会话的历史消息文件

#5.工具函数：get_history
封装 FileChatMessageHistory 的实例化逻辑，
固定存储路径为 ./chat_history，对外提供「根据 session_id 获取会话历史对象」的统一入口。
"""
import json
import logging
import os
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

logger = logging.getLogger(__name__)


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, storage_path: str):
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path, f"{self.session_id}.json")

        os.makedirs(self.storage_path, exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        old_messages = self.messages
        all_messages = old_messages + list(messages)

        new_messages = [message_to_dict(message) for message in all_messages]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)

        logger.info(
            "chat history saved | session_id=%s | message_count=%d | file=%s",
            self.session_id,
            len(all_messages),
            self.file_path,
        )

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                message_data = json.load(f)
            return messages_from_dict(message_data)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.warning(
                "chat history json decode failed | session_id=%s | file=%s",
                self.session_id,
                self.file_path,
            )
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

        logger.info(
            "chat history cleared | session_id=%s | file=%s",
            self.session_id,
            self.file_path,
        )


def get_history(session_id: str) -> FileChatMessageHistory:
    return FileChatMessageHistory(session_id=session_id, storage_path="./chat_history")