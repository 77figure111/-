#这个文件放请求和响应模型。
from pydantic import BaseModel, Field

"""
BaseModel帮你自动校验数据、自动转类型、自动生成接口文档
"""
#请求体,Field类型注解默认值为...
## 1. 前端传给后端的数据格式（请求体）
#作用：后端会自动校验前端传的对不对，少传、传错都会直接报错，不用你写 if 判断。
class ChatRequest(BaseModel):
    thread_id: str=Field(...,description="会话线程ID")
    message: str = Field(..., min_length=1, description="用户输入")

## 2. 后端返回给前端的回答格式
#作用：规定后端必须返回 {"answer": "xxx"} 这种格式，前端好解析
class ChatResponse(BaseModel):
    answer: str

#3. 健康检查返回格式
#一般用于：服务器活着吗？接口通不通？返回格式：json，{"status": "ok"}
class HealthResponse(BaseModel):
    status: str