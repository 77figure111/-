"""
基于streamlit完成WEB网页上传服务
"""
import os
import sys

from fastapi import requests

sys.path.append(".")  # 往上退一级目录
import streamlit as st
import dotenv
dotenv.load_dotenv()

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8001/ingest/file")

st.set_page_config(page_title="知识库更新服务",page_icon="📚", layout="centered")
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

def upload_file_to_backend(upoaded_file,doc_type:str,product_name: str, category: str):
    files={
        #"text/plain" 是 MIME 类型（文件的媒体类型）,兜底 / 默认值逻辑：,纯文本文件
        "file":(upoaded_file.name,upoaded_file.getvalue(),upoaded_file.type or "text/plain")
    }
    data = {
        "doc_type": doc_type,
        "product_name": product_name,
        "category": category,
    }
    resp=requests.post(INGEST_URL, files=files, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

if uploader_file :
    #提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024
    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")
    # 获取内容
    try:
        preview_text=uploader_file.getvalue().decode("utf-8")
    except UnicodeError:
        preview_text="该文件不是 UTF-8 编码，无法直接预览。"

    st.text_area("文件内容预览", preview_text, height=240)
    # 导入按钮
    if st.button(f"导入：{file_name}", type="primary"):
        try:
            with st.spinner("正在上传并写入知识库..."):
                result = upload_file_to_backend(
                    uploaded_file=uploader_file,
                    doc_type=doc_type,
                    product_name=product_name,
                    category=category,
                )
            st.success("导入成功")
            st.json(result)
        except requests.exceptions.Timeout:
            st.error("上传超时，请稍后重试。")
        except requests.exceptions.RequestException as e:
            st.error(f"上传失败：{e}")
        except Exception as e:
            st.error(f"未知错误：{e}")
        # with st.spinner("知识库载入中。。。"): #在spinner内的代码执行过程中，会有一个转圈动画
        #     #time.sleep(1)
        #     result=st.session_state["service"].upload_by_str(text,file_name)
        #     st.success(f"导入完成：{file_name}")
        #     st.write(result)
