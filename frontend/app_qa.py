"""
只做三件事：
保存聊天记录
保存 thread_id
把用户消息发给 AgentService
"""
import uuid
import streamlit as st


import requests
# 后续改为从环境变量读取
API_URL = "http://localhost:8001/chat"
#写一个“调用后端API函数”
def ask_backend(message, thread_id):
    try:
        resp=requests.post(
                           API_URL,
                           json={
                               "message": message,
                               "thread_id": thread_id
                           },
                           timeout=60
                          )
        # raise_for_status()是requests / httpx 库的方法
        # 只要 HTTP 响应状态码是 4xx（客户端错误）或 5xx（服务端错误），就直接抛出异常，让程序报错停止。
        resp.raise_for_status()
        data=resp.json()
        return data.get("answer", "后端返回格式异常，缺少 answer 字段")
    except requests.exceptions.RequestException as e:
        return f"后端请求失败: {e}"
    except ValueError:
        return "后端返回的不是合法 JSON"
    except Exception as e:
        return f"未知错误: {e}"



#标题
st.title("智能客服")
st.divider()
#1,初始化thread_id（记忆id）
if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=str(uuid.uuid4())
#2. 初始化消息列表
if "message" not in st.session_state:
    st.session_state["message"] = [
        {"role": "assistant", "content": "你好，我是购物助手，有什么可以帮助你？"}
    ]


# 4. 初始化清空状态

if "clear_confirm" not in st.session_state:
    st.session_state["clear_confirm"] = False
## 渲染历史消息

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
# 清空聊天按钮
if st.button("清空当前聊天"):
    st.session_state["clear_confirm"] = True
if st.session_state["clear_confirm"]:
    st.warning("确定要清空所有聊天记录吗？此操作不可恢复！")
    if st.button("确定要清空", type="primary"):
         # 关键：生成新的 thread_id，相当于开启一段新会话
         st.session_state["thread_id"]=str(uuid.uuid4())
         st.session_state["message"] = [
             {"role": "assistant", "content": "你好，我是购物助手，有什么可以帮助你？"}
         ]
         st.session_state["clear_confirm"] = False
         st.rerun()
    elif st.button("取消"):
        st.session_state["clear_confirm"] = False
        st.rerun()
## 用户输入框
prompt = st.chat_input("请输入您的问题")
if prompt:
    with st.spinner("小助手思考中"):
        st.chat_message("user").write(prompt)
        answer = ask_backend(
            prompt,
            st.session_state.thread_id
        )
        st.chat_message("assistant").write(answer)
        # 保存到历史
        st.session_state["message"].append({"role": "user", "content": prompt})
        st.session_state["message"].append({"role": "assistant", "content": answer})

