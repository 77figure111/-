#基于本地 JSON 文件的会话历史存储
import json
import os.path
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id=session_id
        self.storage_path=storage_path#文件夹路径
        self.file_path=os.path.join(self.storage_path, f"{self.session_id}.json")
        #确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)


    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        #Sequence序列 类似于list，tuple
        old_messages=self.messages
        all_messages=old_messages+list(messages)
        """
        将数据同步写入本地文件中
        类对象写入文件->一堆二进制
        为了方便，可以将BaseMessage消息转成字典（借助json模块以json字符串写入文件）
        """

        new_messages=[message_to_dict(message) for message in all_messages]
        #将数据写入文件
        with open(self.file_path,"w",encoding="utf-8")as f:
            #json.dump 加中文和缩进
            json.dump(new_messages,f,ensure_ascii=False, indent=2)

    #获取消息,@property装饰器将messages方法变成成员变量，r是读模型
    @property
    def messages(self)->list[BaseMessage]:
        try:
            with open(self.file_path,"r",encoding="utf-8")as f:
                message_data=json.load(f)#返回值就是list[字典]
            return messages_from_dict(message_data)
        except FileNotFoundError:
            return []

    #清除消息
    def clear(self):
        with open(self.file_path,"w",encoding="utf-8")as f:
            json.dump([],f, ensure_ascii=False, indent=2)

def get_history(session_id):
    return FileChatMessageHistory(session_id, storage_path="../../chat_history")



