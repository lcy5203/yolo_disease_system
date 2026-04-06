from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.auth import get_current_user
from app.db.models import User
from app.services import ai_service
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    last_result: dict = None

@router.post("/chat")
async def chat_with_expert(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    农作物 AI 专家在线交流端点
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="请输入问题内容")
    
    # 模拟真实专家响应感，调用 RAG 逻辑
    answer = await ai_service.ask_agro_expert(db, request.query, request.last_result)
    
    return {
        "user": current_user.username,
        "answer": answer,
        "role": "AI 农业专家 (DeepSeek-RAG 版)"
    }
