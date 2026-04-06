from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import DetectionRecord

router = APIRouter()

@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    # Total detections
    total_detections = db.query(DetectionRecord).count()
    
    # Top 5 diseases
    top_5_diseases = db.query(
        DetectionRecord.disease_name,
        func.count(DetectionRecord.id).label("count")
    ).group_by(DetectionRecord.disease_name).order_by(func.count(DetectionRecord.id).desc()).limit(5).all()
    
    # Simple list format for chart
    chart_data = [{"name": r[0], "value": r[1]} for r in top_5_diseases]
    
    return {
        "total_detections": total_detections,
        "top_diseases": chart_data
    }
