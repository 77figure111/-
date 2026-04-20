"""
早期 RAG 编排实验版本。
当前正式主链路不使用本文件。
正式聊天入口统一走 app.services.agent_service.AgentService。
"""



from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from file_history_store import get_history
from app.services.escalation_service import should_escalate
from app.services.order_extractor import extract_order_id
from app.services.order_service import get_order_status, get_logistics_status, get_refund_status
from app.services.query_classifier import classify_query
from app.services.response_guard import check_need_followup
from app.services.vector_stores import VectorStoreService
from app.services.knowledge_base import embed_model
from dotenv import load_dotenv
load_dotenv()
#打印一下最终提示词
def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

chat_model=ChatOpenAI(model="gpt-5-mini")

# def format_document(docs:list[Document]):
#     if not docs:
#         return "无相关资料"
#     formatted_parts=[]
#     for i,doc in enumerate(docs,start=1):
#         source=doc.metadata.get("source","未知来源")
#         doc_type=doc.metadata.get("doc_type","未知类型")
#         product_name=doc.metadata.get("product_name","")
#         category=doc.metadata.get("category","")
#         formatted_parts.append(
#             f"【资料{i}\n】"
#             f"来源: {source}\n"
#             f"类型: {doc_type}\n"
#             f"商品: {product_name}\n"
#             f"类别: {category}\n"
#             f"内容：{doc.page_content}"
#         )
#         return "\n".join(formatted_parts)

class RagService(object):
    def __init__(self):
        self.vector_service=VectorStoreService(embedding=embed_model)
        self.prompt_template=ChatPromptTemplate.from_messages([
            ("system","""
            你是一名购物软件智能客服，主要处理以下问题：
            1.商品信息咨询
            2.尺码/适用人群咨询
            3.活动规则咨询
            4.物流配送咨询
            5.售后与退换货政策咨询
            回答规则：
            -必须优先依赖我提供的参考资料回答，不要脱离资料乱编。
            -如果资料不足，请明确说“我目前没有足够依赖回答这个问题”。
            -如果用户的问答信息不完整，比如问尺码但是没有给身高体重，请先追问再回答。
            -回答风格要简洁，礼貌，像电商客服。
            -回答最后尽量附上“参考来源”
            参考资料：{context}"""),
            ("system","并且我提供的用户对话历史记录，如下:"),
            MessagesPlaceholder("history"),
            ("user","请回答用户的提问：{input}")
        ])

        self.chat_model=chat_model
        self.chain=self.__get_chain()
    #专门做“回答前判断”
    def pre_check(self,user_input:str):
        followup_result=check_need_followup(user_input)
        #1.如果返回的时None，说明不需要追问，直接继续
        if followup_result is None:
            return {"action":"continue"}
        #2.如果返回的不是字典，也按继续处理，避免程序报错
        if not isinstance(followup_result,dict):
            return {"action":"continue"}
        #3.安全读取 action，默认 continue
        action=followup_result.get("action", "continue")
        if action !="continue":
            return followup_result
        return {"action":"continue"}
    def answer_by_tool(self,user_input:str,pending_query_type=None):
        #1.先清洗输入，去掉句末常见标点
        cleaned_input=user_input.strip()
        cleaned_input = cleaned_input.replace("。", "").replace("，", "")
        cleaned_input = cleaned_input.replace(".", "").replace(",", "")
        #2.识别问题类型+提取订单号
        query_type=classify_query(cleaned_input)
        order_id=extract_order_id(cleaned_input)
        valid_query_types = ["order_query", "logistics_query", "refund_query"]
        #3.  如果当前句没识别出意图，但提取到了订单号，# 且上一轮正在等待订单号，就沿用上一轮意图
        if order_id and query_type not in valid_query_types and pending_query_type in valid_query_types:
            query_type = pending_query_type

        # 4. 如果识别到了订单/物流/退款类，但没给订单号，先追问
        if query_type in valid_query_types and not order_id:
            return {
                "answer":"为了帮您准确查询，请提供订单号，例如 JD10001。",
                "pending_query_type":query_type
            }

        # 5. 查询订单状态
        if query_type=="order_query":
            info=get_order_status(order_id)
            if info:
                return {
                    "answer":f"订单{order_id},当前状态：{info['status']},商品：{info['product_name']}，下单时间：{info['created_at']}。",
                    "pending_query_type":None
                }

            return {
                "answer":f"抱歉，没有查询到订单 {order_id} 的信息。",
                "pending_query_type":None
            }
        # 6. 查询物流状态
        if query_type == "logistics_query":
            info = get_logistics_status(order_id)
            if info:
                return {
                "answer": f"订单 {order_id} 当前物流状态：{info['logistics_status']}，当前位置：{info['current_location']}，预计送达时间：{info['estimated_delivery']}。",
                "pending_query_type": None
            }
            return {
            "answer": f"抱歉，没有查询到订单 {order_id} 的物流信息。",
            "pending_query_type": None
        }
        # 7. 查询退款状态
        if query_type == "refund_query":
            info = get_refund_status(order_id)
            if info:
                return {
                "answer": f"订单 {order_id} 当前退款状态：{info['refund_status']}，退款金额：{info['refund_amount']} 元，最近更新时间：{info['updated_at']}。",
                "pending_query_type": None
            }
            return {
            "answer": f"抱歉，没有查询到订单 {order_id} 的退款信息。",
            "pending_query_type": None
        }
        # 8. 不是工具类问题，返回 None，交给 RAG
        return None


    #最终回答函数：answer
    def answer(self,user_input:str,session_config:dict,pending_query_type=None):
        # 第一步：先做预处理检查
        precheck=self.pre_check(user_input)
        if precheck["action"]=="followup":
            return {
                "answer":precheck.get("message","请补充必要信息。"),
                "pending_query_type": pending_query_type
            }
        # 如果不需要追问，才执行下面的AI回答
        #2.判断是否是工具类问题（订单/物流/退款）
        tool_result=self.answer_by_tool(user_input,pending_query_type)
        if tool_result is not None:
            final_answer = tool_result["answer"]
            #判断是否走人工
            if should_escalate(user_input, final_answer):
                final_answer += "\n\n如果您需要，我建议为您转人工客服进一步处理。"
            return {
            "answer": final_answer,
            "pending_query_type": tool_result["pending_query_type"]
        }
        #3.否则走rag
        result=self.chain.invoke({"input":user_input},session_config)
        if should_escalate(user_input, result):
            result += "\n\n如果您需要，我建议为您转人工客服进一步处理。"
        return  {
        "answer": result,
        "pending_query_type": None
    }

    def __get_chain(self):
        """获取最终的执行链"""
        retriever=self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关资料"
            formatted_parts = []
            for i, doc in enumerate(docs, start=1):
                source = doc.metadata.get("source", "未知来源")
                doc_type = doc.metadata.get("doc_type", "未知类型")
                product_name = doc.metadata.get("product_name", "")
                category = doc.metadata.get("category", "")
                formatted_parts.append(
                    f"【资料{i}\n】"
                    f"来源: {source}\n"
                    f"类型: {doc_type}\n"
                    f"商品: {product_name}\n"
                    f"类别: {category}\n"
                    f"内容：{doc.page_content}"
                )
            return "\n".join(formatted_parts)

        # def format_for_retriever(value):
        #     print("____", value)
        #     return value["input"]
        # def format_for_template(value):
        #     #{input,context,history}
        #     new_value={}
        #     new_value["input"]=value["input"]["input"]
        #     new_value["context"]=value["context"]
        #     new_value["history"]=value["input"]["history"]
        #     return new_value



        # chain=(
        #     {
        #         "input":RunnablePassthrough(),
        #         #字典里面也接收history,但是直接写history会报错，直接写成函数
        #         #"history": lambda x:x["history"],
        #         "context": RunnableLambda(format_for_retriever)  | retriever | format_document
        #     } | RunnableLambda(format_for_template) | self.prompt_template | self.chat_model |StrOutputParser()
        #     )
        # def debug_input(x):
        #     print("进入 assign 前:", x)
        #     return x["input"]
        #
        # def debug_context(x):
        #     print("检索后的 context:\n", x[:500] if isinstance(x, str) else x)
        #     return x
        #
        # def debug_prompt(prompt_value):
        #     print("=" * 30)
        #     print(prompt_value.to_string()[:1500])
        #     print("=" * 30)
        #     return prompt_value
        """
        这里的 input 会被 Python 解析成内置函数，
        不会自动理解成“取字典键 input”。Python 里名字解析就是按变量名/函数名处理，
        不会把裸写的 input 当成 x["input"]。
        内置函数 input() 也确实存在于标准内置函数集合里
        """
        chain = (
                RunnablePassthrough().assign(
                    context=RunnableLambda(lambda x: x["input"]) | retriever | format_document
                )
                | self.prompt_template
                | self.chat_model
                | StrOutputParser()
        )


        """
        chain=(
            {
                "input":RunnablePassthrough(),
                "context":retriever | format_document
            } | self.prompt_template | print_prompt | self.chat_model |StrOutputParser()
            )
        """
        #增强链，添加记忆功能
        conversation_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return conversation_chain

