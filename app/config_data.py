from pathlib import Path


md5_path= "../md5.txt"

#向量存储的实例Chroma向量库对象
collection_name="rag_knowledge_base"
persist_direction="./chroma_db"
#分割器
chunk_size=1000
chunk_overlap=100
separators=["\n\n","\n"," ",""]
max_split_char_number=1000   #文本分割的阈值，超过这个值才会被分割


#检索器
#similarity_threshold=2#检索返回的文档数量
# 检索器返回的文档条数
retrieval_top_k = 3



# session_id配置
def build_session_config(session_id:str):
    return {
    "configurable": {"session_id": session_id}
}
#数据处理路径
BASE_DIR=Path(__file__).parent
PROJECT_ROOT = BASE_DIR
SAVE_DIR=PROJECT_ROOT/"data"/"raw"/"chinese_ecomqa"

#RunnableConfig = {"configurable": {"thread_id": "1"}}