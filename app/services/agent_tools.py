import logging
import time

from langchain_core.documents import Document
from langchain_core.tools import tool

from app.services.knowledge_base import embed_model
from app.services.order_service import get_order_status, get_logistics_status, get_refund_status
from app.services.vector_stores import VectorStoreService

logger = logging.getLogger(__name__)
# ====== 知识库检索器（只初始化一次）======
_vector_service=VectorStoreService(embedding=embed_model)
_retriever=_vector_service.get_retriever()

#把检索到的文档整理成大模型更容易读的文本。
def _format_docs(docs: list[Document]):
    if not docs:
        return "无相关资料"
    parts = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "未知来源")
        doc_type = doc.metadata.get("doc_type", "未知类型")
        product_name = doc.metadata.get("product_name", "")
        category = doc.metadata.get("category", "")
        parts.append(
            f"【资料{i}\n】"
            f"来源: {source}\n"
            f"类型: {doc_type}\n"
            f"商品: {product_name}\n"
            f"类别: {category}\n"
            f"内容：{doc.page_content}"
        )
    return "\n".join(parts)

@tool
def search_knowledge_base(question:str)->str:
    """
    搜索知识库
    适用于商品信息、尺码建议、活动规则、物流政策、售后政策等问题。
    如果问题不是订单系统状态查询，优先使用这个工具
    :param question:用户问题
    :return:str
    """
    logger.info(
        "tool called | name=search_knowledge_base | question_len=%d | preview=%s",
        len(question),
        question[:60].replace("\n", " "),
    )
    t0 = time.perf_counter()
    docs=_retriever.invoke(question)
    elapsed = time.perf_counter() - t0

    logger.info(
        "tool finished | name=search_knowledge_base | doc_count=%d | elapsed=%.3fs",
        len(docs),
        elapsed,
    )
    return _format_docs(docs)

@tool
def query_order_status(order_id:str)->str:
    """
    查询订单当前状态,仅当你已经拿到明确的订单号时使用，例如 JD10001。
    :param order_id: 订单号
    :return:商品信息
    """
    logger.info("tool called | name=query_order_status | order_id=%s", order_id)
    info = get_order_status(order_id)
    if info:
        logger.info("tool finished | name=query_order_status | found=true | order_id=%s", order_id)
        return (
            f"订单 {order_id} 当前状态：{info['status']}，"
            f"商品：{info['product_name']}，"
            f"下单时间：{info['created_at']}。"
        )
    logger.info("tool finished | name=query_order_status | found=false | order_id=%s", order_id)
    return f"抱歉，没有查询到订单 {order_id} 的信息。"


@tool
def query_logistics_status(order_id: str) -> str:
    """
    查询订单物流状态。仅当你已经拿到明确的订单号时使用，例如 JD10001。
    :param order_id:
    :return:
    """
    logger.info("tool called | name=query_logistics_status | order_id=%s", order_id)
    info = get_logistics_status(order_id)
    if info:
        logger.info("tool finished | name=query_logistics_status | found=true | order_id=%s", order_id)
        return (
            f"订单 {order_id} 当前物流状态：{info['logistics_status']}，"
            f"当前位置：{info['current_location']}，"
            f"预计送达时间：{info['estimated_delivery']}。"
        )
    logger.info("tool finished | name=query_logistics_status | found=false | order_id=%s", order_id)
    return f"抱歉，没有查询到订单 {order_id} 的物流信息。"
@tool
def query_refund_status(order_id: str) -> str:
    """
    查询订单退款状态。仅当你已经拿到明确的订单号时使用，例如 JD10001。
    """
    logger.info("tool called | name=query_refund_status | order_id=%s", order_id)
    info = get_refund_status(order_id)
    if info:
        logger.info("tool finished | name=query_refund_status | found=true | order_id=%s", order_id)
        return (
            f"订单 {order_id} 当前退款状态：{info['refund_status']}，"
            f"退款金额：{info['refund_amount']} 元，"
            f"最近更新时间：{info['updated_at']}。"
        )
    logger.info("tool finished | name=query_refund_status | found=false | order_id=%s", order_id)
    return f"抱歉，没有查询到订单 {order_id} 的退款信息。"
