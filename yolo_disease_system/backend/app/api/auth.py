from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserLogin, UserResponse

router = APIRouter()

@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or user.hashed_password != user_data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    return {
        "token": "mock_token_for_now", 
        "role": user.role, 
        "username": user.username
    }
