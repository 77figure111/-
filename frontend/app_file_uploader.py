"""
基于streamlit完成WEB网页上传服务
"""
import sys
sys.path.append(".")  # 往上退一级目录
import streamlit as st
from app.services.knowledge_base import KnowledgeBaseService
import dotenv
dotenv.load_dotenv()


st.title("知识库更新服务")

#文件上传
uploader_file=st.file_uploader(
    label="请上传txt或json文件",
    type=['txt','md'],
    accept_multiple_files=False#accept_multiple_files=True → 返回 列表,支持【同时选择多个文件】一起上传
)
doc_type=st.selectbox(
    "请选择文件类型",
    ["faq","product","policy","promotion","logistics"]
)
product_name=st.text_input("商品名（可选）",value="")
category=st.text_input("商品类别（可选）",value="通用")
if "service"not in st.session_state:
    st.session_state["service"]=KnowledgeBaseService()


if uploader_file :
    #提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024
    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")
    # 获取内容
    text = uploader_file.getvalue().decode("utf-8")
    st.text_area("文件内容预览", text, height=200)
    # 导入按钮
    if st.button(f"导入：{file_name}"):
        with st.spinner("知识库载入中。。。"): #在spinner内的代码执行过程中，会有一个转圈动画
            #time.sleep(1)
            result=st.session_state["service"].upload_by_str(text,file_name)
            st.success(f"导入完成：{file_name}")
            st.write(result)
