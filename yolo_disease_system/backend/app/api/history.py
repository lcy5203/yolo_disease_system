from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.session import get_db
from app.models.models import DetectionRecord, Encyclopedia
from app.schemas.schemas import HistoryRecord, EncyclopediaItem

router = APIRouter()

@router.get("/history", response_model=List[HistoryRecord])
async def get_history(db: Session = Depends(get_db)):
    records = db.query(DetectionRecord).order_by(DetectionRecord.timestamp.desc()).limit(20).all()
    return records

@router.get("/encyclopedia", response_model=List[EncyclopediaItem])
async def get_ency(db: Session = Depends(get_db)):
    return db.query(Encyclopedia).all()

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    stats = db.query(DetectionRecord.disease_name, func.count(DetectionRecord.id).label('total'))\
              .group_by(DetectionRecord.disease_name)\
              .order_by(func.count(DetectionRecord.id).desc()).limit(5).all()
    return [{"name": s[0], "value": s[1]} for s in stats]
