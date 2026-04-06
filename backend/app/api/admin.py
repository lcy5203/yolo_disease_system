from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, DiseaseEncyclopedia, DetectionRecord
from app.api.auth import get_current_user
from pydantic import BaseModel
import os
import json

router = APIRouter()

# 校验管理员身份的依赖
def check_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足：仅限管理员访问")
    return user

class EncyclopediaUpdate(BaseModel):
    causes: str = None
    prevention: str = None
    crop_type: str = None

class ModelUpdate(BaseModel):
    model_path: str # 例如 models/best_v2.pt
    is_attention: bool = False

# 1. 更新防治建议
@router.put("/encyclopedia/{item_id}", dependencies=[Depends(check_admin)])
def update_disease_info(item_id: int, info: EncyclopediaUpdate, db: Session = Depends(get_db)):
    db_item = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="未找到该病害词条")
    
    if info.causes: db_item.causes = info.causes
    if info.prevention: db_item.prevention = info.prevention
    if info.crop_type: db_item.crop_type = info.crop_type
    
    db.commit()
    return {"msg": f"病害 {db_item.name} 信息已更新"}

# 2. 更换模型路径 (持久化到 active_model.json)
@router.post("/model/switch", dependencies=[Depends(check_admin)])
def switch_system_model(config: ModelUpdate):
    config_path = "models/active_model.json"
    
    # 物理检查模型文件是否存在
    if not os.path.exists(config.model_path):
        raise HTTPException(status_code=400, detail=f"物理路径中找不到模型文件: {config.model_path}")

    new_config = {
        "base_model": config.model_path if not config.is_attention else "models/best.pt",
        "attention_model": config.model_path if config.is_attention else "models/yolov11_attention.pt"
    }

    with open(config_path, "w") as f:
        json.dump(new_config, f)
    
    return {"msg": "系统模型路径已更新，下次检测将生效", "active_config": new_config}

# 3. 管理员概览数据 (敏感数据)
@router.get("/users/count", dependencies=[Depends(check_admin)])
def get_user_count(db: Session = Depends(get_db)):
    count = db.query(User).count()
    return {"total_users": count}
