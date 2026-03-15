from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from app.db.session import get_db
from app.services.yolo_engine import yolo_engine
from app.models.models import DetectionRecord, Encyclopedia
from app.core.config import settings

router = APIRouter()

@router.post("/detect")
async def detect_disease(file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"{settings.UPLOAD_DIR}/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    detections = yolo_engine.detect(file_path)
    
    main_disease = detections[0]["class"] if detections else "Unknown"
    confidence = detections[0]["confidence"] if detections else 0.0
    
    # Matching Encyclopedia
    info = db.query(Encyclopedia).filter(Encyclopedia.disease_name.contains(main_disease)).first()
    
    # Save to history
    new_record = DetectionRecord(
        image_path=file_path,
        disease_name=main_disease,
        confidence=confidence,
        crop_type="Unknown"
    )
    db.add(new_record)
    db.commit()

    return {
        "status": "success",
        "image_url": f"http://localhost:8000/{file_path}",
        "detections": detections,
        "main_disease": main_disease,
        "cause": info.cause if info else "未知原因",
        "treatment": info.treatment if info else "请咨询专家"
    }
