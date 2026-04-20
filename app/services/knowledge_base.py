"""
知识库
"""
from datetime import datetime
import os


from langchain_openai import OpenAIEmbeddings

from app import config_data as config
import hashlib
from langchain_chroma import Chroma

from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()


def check_md5(md5_str:str):
    #检查传入的md5字符串是否已经存在
    #return False表示md5未处理，True表示已处理，已有记录
    if not os.path.exists(config.md5_path):
        #如果文件不存在，那表示没有处理过md5
        #创建这个文件，python中只要打开，并是‘w’模型，再关闭就创建了文件
        open(config.md5_path,'w',encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line=line.strip()#处理字符串前后的空格和回车
            if line == md5_str:
                return True
        return False


def save_md5(md5_str:str):
    #将传入的md5字符串，记录到文件内保存
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str+'\n')


def get_string_md5(input_str:str,encoding='utf-8'):
    #将传入的字符串转换为md5字符串
    #步骤1：将字符串转换为bytes字节数组，utf-8是把字符串转为字节数组的规则
    str_bytes=input_str.encode(encoding=encoding)
    #创建md5对象
    md5_obj=hashlib.md5()#得到md5对象
    md5_obj.update(str_bytes)#更新内容（传入即将要转换的字节数组）(把字节数组丢进 MD5 计算器里进行计算)
    md5_hex=md5_obj.hexdigest()#把算好的 MD5 值，转成32 位小写十六进制字符串
    return md5_hex

embed_model=OpenAIEmbeddings(model="text-embedding-3-small")

class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件夹不存在就创建，如果存在就跳过
        os.makedirs(config.persist_direction,exist_ok=True)
        #向量存储的实例Chroma向量库对象
        self.chroma=Chroma(collection_name=config.collection_name,#数据库表名
                           embedding_function=embed_model,#嵌入模型
                           persist_directory=config.persist_direction, #数据库本地存储文件夹
                           )
        self.spliter=RecursiveCharacterTextSplitter(chunk_size=config.chunk_size,
                                                    chunk_overlap=config.chunk_overlap,
                                                    separators=config.separators,
                                                    length_function=len
        )#文本分割的对象


    def upload_by_str(self,
                      data:str,
                      filename:str,
                      doc_type:str="faq",
                      product_name:str="",
                      category:str="通用")->str:
        #将传入的字符串，进行向量化，存入向量数据库中
        #先得到传入字符串的md5值
        md5_hex=get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存入知识库中"

        if len(data)>config.max_split_char_number:
            # 就用分割器把长文本切成多个小片段，存到列表里
            knowledge_chunks: list[str]=self.spliter.split_text(data)
        else:
            # 直接把整个文本作为唯一一个片段放进列表
            knowledge_chunks=[data]

        metadata={
            "source":filename,
            "doc_type":doc_type,
            "product_name":product_name,
            "category":category,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"小高"
        }
        #加载到向量库
        self.chroma.add_texts(
            knowledge_chunks,
            #不同的chunks各自的元数据
            metadatas=[metadata for _ in knowledge_chunks]
        )
        #记录到md5文件中
        save_md5(md5_hex)
        return "[成功]内容已经成功载入到向量库中"


# if __name__ == "__main__":
#     service=KnowledgeBaseService()
#     r=service.upload_by_str("周杰伦","textfile")
#     print(r)