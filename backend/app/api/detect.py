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

def get_resource_path(relative_path):
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

def get_active_model_path():
    """读取当前系统指定的唯一权重路径"""
    config_path = get_resource_path("models/active_model.json")
    default_path = "models/yolo11s_ema_mpdiou.pt"
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                # 兼容旧格式或新格式，优先取 model_path
                return config.get("model_path") or config.get("attention_model") or default_path
    except:
        pass
    return default_path

# 全局模型缓存
models_cache = {}

def get_model():
    """获取系统核心识别模型"""
    path = get_active_model_path()
    
    if path not in models_cache:
        absolute_path = get_resource_path(path)
        print(f"[SYSTEM] 正在初始化核心模型: {absolute_path}")
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"找不到权重文件: {absolute_path}")
        
        try:
            models_cache[path] = YOLO(absolute_path)
            print(f"[SUCCESS] 模型加载就绪！")
        except Exception as e:
            print(f"[ERROR] 加载失败: {str(e)}")
            raise e
            
    return models_cache[path]

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# 8 类病害的中英映射表 (精简匹配实际数据集)
DISEASE_MAP = {
    "Apple___Apple_scab": "苹果黑星病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果雪松赤星病",
    "Apple___healthy": "苹果健康叶片",
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄褐斑病 (黑豆病)",
    "Grape___healthy": "葡萄健康叶片",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病"
}

@router.post("/")
async def start_detection(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. 保存原始图片
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        img_save_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(img_save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # 2. 执行模型推理
        import time
        start_time = time.perf_counter()
        
        yolo_model = get_model()
        results = yolo_model.predict(img_save_path, conf=0.25)
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # 3. 数据解析与入库
        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0]
            cls_id = int(box.cls[0])
            cls_name_en = results[0].names[cls_id]
            cls_name_zh = DISEASE_MAP.get(cls_name_en, cls_name_en)
            confidence = float(box.conf[0])
            
            # 保存标注结果图 (采用 plots 渲染 + cv2 保存，兼容性最强)
            res_img_filename = f"res_{unique_filename}"
            res_img_path = os.path.join(UPLOAD_DIR, res_img_filename)
            
            # 渲染标注框并转换为 BGR 格式保存
            annotated_frame = results[0].plot() # 得到的是 RGB numpy array
            cv2.imwrite(res_img_path, annotated_frame) 
            
            # 获取专家建议 (防错：如果数据库没准备好，不应卡死)
            try:
                disease_info = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.name == cls_name_zh).first()
            except:
                disease_info = None
            
            # 作物分类逻辑
            crop_type = "苹果" if "Apple" in cls_name_en else ("葡萄" if "Grape" in cls_name_en else "其他")
            
            record = DetectionRecord(
                user_id=current_user.id,
                disease_name=cls_name_zh,
                confidence=confidence,
                original_image=f"/static/uploads/{unique_filename}",
                result_image=f"/static/uploads/{res_img_filename}",
                model_name="YOLO11s-EMA",
                crop_type=crop_type,
                inference_time=float(latency_ms)
            )
            db.add(record)
            db.commit()
            
            return {
                "id": record.id,
                "disease_name": cls_name_zh,
                "confidence": confidence,
                "inference_time": round(latency_ms, 2),
                "model_name": "YOLO11s-EMA",
                "original_image": record.original_image,
                "result_image": record.result_image,
                "causes": disease_info.causes if disease_info else "系统正在分析病因...",
                "prevention": disease_info.prevention if disease_info else "建议加强环境通风并观察病情。"
            }
        
        return {
            "disease_name": "未检测到显著病害", 
            "confidence": 0, 
            "original_image": f"/static/uploads/{unique_filename}", 
            "result_image": "", 
            "causes": "图像健康或特征不明显。", 
            "prevention": "维持常规养护即可。"
        }

    except Exception as e:
        import traceback
        print(f"[FATAL] 识别流程崩溃: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")
