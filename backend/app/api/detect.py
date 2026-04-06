from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from ultralytics import YOLO
import os
import shutil
import uuid
import datetime
import sys
import cv2
import json
import PIL.Image as Image
from app.db.session import get_db
from app.db.models import DetectionRecord, User, DiseaseEncyclopedia
from app.api.auth import get_current_user
from app.core import security

router = APIRouter()

# Directories
UPLOAD_DIR = "static/uploads"

# 处理 PyInstaller 打包后的文件路径
def get_resource_path(relative_path):
    # 获取 detect.py 所在的后端根目录 (detect.py 在 app/api/, 需要向上跳三级)
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

def get_active_config():
    """从本地 JSON 读取当前生效的模型路径"""
    config_path = get_resource_path("models/active_model.json")
    default = {"base_model": "models/best.pt", "attention_model": "models/yolov11_attention.pt"}
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except:
        pass
    return default

# 全局模型缓存
models_cache = {}

def get_model(use_attention: bool):
    config = get_active_config()
    path = config["attention_model"] if use_attention else config["base_model"]
    
    if path not in models_cache:
        absolute_path = get_resource_path(path)
        if not os.path.exists(absolute_path):
            if use_attention:
                print(f"WARNING: 注意力模型 {path} 尚未就绪...")
                return get_model(False)
            raise FileNotFoundError(f"权重文件 {absolute_path} 不存在。")
        models_cache[path] = YOLO(absolute_path)
    return models_cache[path]

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# 12 类病害的中英映射表
DISEASE_MAP = {
    "Apple___Apple_scab": "苹果黑星病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果雪松赤星病",
    "Apple___healthy": "苹果健康叶片",
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄褐斑病 (黑豆病)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病",
    "Grape___healthy": "葡萄健康叶片",
    "Corn___Common_rust": "玉米锈病",
    "Corn___Gray_leaf_spot": "玉米大斑病 (灰斑病)",
    "Corn___Northern_Leaf_Blight": "玉米北叶枯病",
    "Corn___healthy": "玉米健康叶片"
}

@router.post("/")
async def start_detection(
    image: UploadFile = File(...),
    use_attention: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        img_save_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(img_save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Load Model
        yolo_model = get_model(use_attention)
        
        # Prediction
        results = yolo_model.predict(img_save_path, conf=0.25)
        
        # Parse result
        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0]
            cls_id = int(box.cls[0])
            cls_name_en = results[0].names[cls_id]
            cls_name_zh = DISEASE_MAP.get(cls_name_en, cls_name_en)
            confidence = float(box.conf[0])
            
            res_img_filename = f"res_{unique_filename}"
            res_img_path = os.path.join(UPLOAD_DIR, res_img_filename)
            results[0].save(res_img_path)
            
            # Fetch treatment info from encyclopedia
            disease_info = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.name == cls_name_zh).first()
            
            record = DetectionRecord(
                user_id=current_user.id,
                original_image=f"/static/uploads/{unique_filename}",
                result_image=f"/static/uploads/{res_img_filename}",
                disease_name=cls_name_zh,
                confidence=confidence
            )
            db.add(record)
            db.commit()
            
            return {
                "id": record.id,
                "disease_name": cls_name_zh,
                "confidence": confidence,
                "original_image": record.original_image,
                "result_image": record.result_image,
                "causes": disease_info.causes if disease_info else "暂无专家病因分析",
                "prevention": disease_info.prevention if disease_info else "建议喷洒常规杀菌剂并观察新叶生长情况。"
            }
        
        return {"disease_name": "未检测到显著病害", "confidence": 0, "original_image": f"/static/uploads/{unique_filename}", "result_image": "", "causes": "图像清晰度良好，或当前病症不在数据库覆盖范围内。", "prevention": "保持日常肥水管理。"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
