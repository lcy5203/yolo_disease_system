from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import DetectionRecord

from app.api import auth
from app.db.models import DetectionRecord, User

router = APIRouter()

@router.get("/my")
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    offset = (page - 1) * limit
    records = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id).order_by(DetectionRecord.created_at.desc()).offset(offset).limit(limit).all()
    total = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id).count()
    return {"records": records, "total": total, "page": page}

@router.delete("/{id}")
def delete_history_record(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == id, DetectionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="未找到该历史记录或无权访问")
    db.delete(record)
    db.commit()
    return {"msg": "已成功删除该历史记录"}
