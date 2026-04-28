from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import DetectionRecord, User
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 个人核心指标 (累计次数 + 平均置信度)
    user_stats_query = db.query(
        func.count(DetectionRecord.id).label("total"),
        func.avg(DetectionRecord.confidence).label("avg_conf")
    ).filter(DetectionRecord.user_id == current_user.id).first()

    user_total = int(user_stats_query.total or 0)
    avg_conf = float(user_stats_query.avg_conf or 0)
    
    # 2. 个人病害分布 (用于热力条/图表)
    personal_diseases = db.query(
        DetectionRecord.disease_name,
        func.count(DetectionRecord.id).label("count")
    ).filter(DetectionRecord.user_id == current_user.id)\
     .group_by(DetectionRecord.disease_name).all()
    
    # 3. 个人作物分布 (Apple vs Grape)
    crop_dist = db.query(
        DetectionRecord.crop_type,
        func.count(DetectionRecord.id).label("count")
    ).filter(DetectionRecord.user_id == current_user.id)\
     .group_by(DetectionRecord.crop_type).all()

    # 4. 模型推理性能 (平均耗时)
    perf_stats = db.query(
        DetectionRecord.model_name,
        func.avg(DetectionRecord.inference_time).label("avg_time")
    ).group_by(DetectionRecord.model_name).all()
    
    # 构建前端需要的结构
    return {
        "total_count": user_total,
        "avg_confidence": avg_conf,
        "disease_counts": {r[0]: r[1] for r in personal_diseases},
        "crop_distribution": [{"name": r[0] or "其他", "value": r[1]} for r in crop_dist],
        "performance": [
            {"model": r[0] or "未知", "avg_time": round(r[1], 2) if r[1] else 0} for r in perf_stats
        ]
    }
