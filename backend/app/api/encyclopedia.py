from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import DiseaseEncyclopedia

router = APIRouter()

@router.get("/")
def get_encyclopedia(
    search: str = Query(None),
    crop_type: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(DiseaseEncyclopedia)
    if search:
        query = query.filter(DiseaseEncyclopedia.name.like(f"%{search}%"))
    if crop_type:
        query = query.filter(DiseaseEncyclopedia.crop_type == crop_type)
    
    return query.all()

@router.get("/{id}")
def get_disease_detail(id: int, db: Session = Depends(get_db)):
    disease = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.id == id).first()
    if not disease:
         raise HTTPException(status_code=404, detail="未找到该病害详情")
    return disease
