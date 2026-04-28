from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, DiseaseEncyclopedia
from app.api.auth import get_current_user
from pydantic import BaseModel
import os
import shutil
import uuid
import json

router = APIRouter()

# 权限校验：仅限管理员
def check_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足：仅限管理员访问")
    return user

class EncyclopediaEntry(BaseModel):
    name: str
    crop_type: str
    causes: str = ""
    prevention: str = ""
    image_url: str = ""

# 1. 上传百科展示图
@router.post("/encyclopedia/upload", dependencies=[Depends(check_admin)])
async def upload_encyclopedia_image(file: UploadFile = File(...)):
    FIGURES_DIR = "static/figures"
    if not os.path.exists(FIGURES_DIR):
        os.makedirs(FIGURES_DIR, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    save_name = f"ency_{uuid.uuid4()}{file_ext}"
    save_path = os.path.join(FIGURES_DIR, save_name)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"url": f"/static/figures/{save_name}"}

# 2. 新增病害词条
@router.post("/encyclopedia", dependencies=[Depends(check_admin)])
def create_disease_entry(entry: EncyclopediaEntry, db: Session = Depends(get_db)):
    if db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.name == entry.name).first():
        raise HTTPException(status_code=400, detail="病害名称已存在")
    
    db_item = DiseaseEncyclopedia(**entry.dict())
    db.add(db_item)
    db.commit()
    return {"msg": f"词条 {entry.name} 已创建"}

# 3. 修改病害词条
@router.put("/encyclopedia/{item_id}", dependencies=[Depends(check_admin)])
def update_disease_entry(item_id: int, entry: EncyclopediaEntry, db: Session = Depends(get_db)):
    db_item = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="未找到该病害词条")
    
    db_item.name = entry.name
    db_item.crop_type = entry.crop_type
    db_item.causes = entry.causes
    db_item.prevention = entry.prevention
    if entry.image_url:
        db_item.image_url = entry.image_url
    
    db.commit()
    return {"msg": "词条信息已更新"}

# 4. 删除病害词条
@router.delete("/encyclopedia/{item_id}", dependencies=[Depends(check_admin)])
def delete_disease_entry(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="词条不存在")
    db.delete(db_item)
    db.commit()
    return {"msg": "词条已删除"}

# --- 模型切换逻辑 (保留) ---
class ModelUpdate(BaseModel):
    model_path: str

@router.post("/model/switch", dependencies=[Depends(check_admin)])
def switch_system_model(config: ModelUpdate):
    config_path = "models/active_model.json"
    if not os.path.exists(config.model_path):
        raise HTTPException(status_code=400, detail="文件不存在")
    with open(config_path, "w") as f:
        json.dump({"model_path": config.model_path}, f)
    return {"msg": "核心权重已更新"}
