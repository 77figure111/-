import os
from pathlib import Path

#路径不写死
#md5_path= "../md5.txt"
#数据处理路径
#__file__当前文件自己的路径 services/config_data.py
#.resolve()把路径变成 绝对路径 + 标准化路径，清理乱七八糟的路径符号（比如 . .. 冗余斜杠等）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
#去 .env 或系统环境变量 里找名叫 MD5_FILE 的值
md5_path=os.getenv("MD5_FILE",str(PROJECT_ROOT/"md5.txt"))

#向量存储的实例Chroma向量库对象
collection_name="rag_knowledge_base"
persist_direction=os.getenv("CHROMA_DIR", str(PROJECT_ROOT / "chroma_db"))
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

SAVE_DIR=PROJECT_ROOT/"data"/"raw"/"chinese_ecomqa"

#RunnableConfig = {"configurable": {"thread_id": "1"}}