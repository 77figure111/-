# -
购物软件智能助手
<img width="558" height="451" alt="image" src="https://github.com/user-attachments/assets/5930aaaf-f473-46a3-bd57-663191651eec" />

<img width="547" height="299" alt="image" src="https://github.com/user-attachments/assets/d1dfd37a-4e16-4c00-9aa5-82e99324adad" />

当前正式聊天主链路为：
FastAPI /chat -> AgentService -> tools / knowledge base

experimental/rag.py 为早期实验版本，不参与当前主流程。


# 电商智能客服 Agent

## 项目简介
基于 FastAPI + LangChain + Chroma + Streamlit 的电商智能客服系统，
支持知识库问答、订单查询、物流查询、退款查询和多轮会话。

## 当前主链路
FastAPI /chat -> AgentService -> tools / knowledge base

## 主要能力
- 商品/尺码/活动/政策类知识问答
- 订单状态查询
- 物流状态查询
- 退款状态查询
- thread_id 维度的短期会话记忆

## 启动方式
1. 启动后端
2. 启动前端
3. 上传知识库文件
4. 开始对话

## 说明
experimental/rag.py 为早期实验版本，不参与当前正式主流程。
##项目架构图
Streamlit 前端
↓
FastAPI /chat
↓
AgentService
↓
知识库检索 / 订单工具 / 物流工具 / 退款工具
FastAPI /ingest/file
↓
KnowledgeBaseService
↓
切分 + embedding + Chroma


##技术栈
Python
FastAPI
LangChain
LangGraph 
Agent
Chroma
Streamlit
OpenAI Embeddings 
Chat model
##启动命令

uvicorn app.main:app --reload --port 8001
streamlit run frontend/app_qa.py

##问题举例
这件衣服尺码怎么选

我身高175体重140斤穿什么码

支持七天无理由吗

七天无理由退货运费谁出

帮我查订单JD10001

帮我查一下JD10001物流

JD10003退款进度

我要投诉你们


