"""
FastAPI 官方文件上传推荐使用 UploadFile
支持：
• 文件：txt、md，后面再加 pdf
• 表单字段：doc_type、product_name、category
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.knowledge_base import KnowledgeBaseService

router=APIRouter(prefix="/ingest",tags=["ingest"])
kb_service = KnowledgeBaseService()
@router.post("/file")
async def ingest_file(
        file:UploadFile=File(...),
        doc_type:str=Form("faq"),
        product_name: str = Form(""),#Form(...) = 读取表单数据,Form(值) = 带默认值，Form(...) = 必填
        category: str = Form("通用"),
):
    filename=file.filename or "unknow.txt"
    suffix=filename.lower().split(".")[-1]#提取文件后缀,.split(".") → 按点 . 把名字切成列表,[-1] → 取最后一段 → 就是文件后缀
    if suffix not in {"txt","md"}:
        raise HTTPException(status_code=400,detail="当前仅支持 txt / md 文件")
    raw = await file.read()
    try:
        text=raw.decode("utf-8")
    except UnicodeError:
        raise HTTPException(status_code=400, detail="文件不是 UTF-8 编码")
    result=kb_service.upload_by_str(
        data=text,
        filename=filename,
        doc_type=doc_type,
        product_name=product_name,
        category=category,
    )
    return {"message":result}
"""
然后在 api/main.py 里把它挂上：

from api.routes.ingest import router as ingest_router
app.include_router(ingest_router)
知识库导入就不再依赖 Streamlit 页面了，而是标准 API。
这一步做完，后面：
• 管理后台能调
• 命令行脚本能调
• Docker 容器里也能调
这就叫“可集成”。
"""

