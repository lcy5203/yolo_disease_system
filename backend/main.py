from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ultralytics import YOLO
import shutil
import os
import database as db_mod
import uuid

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO
model = YOLO("yolov8n.pt")

# Dependency for DB session
def get_db():
    db = db_mod.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/login")
async def login(user_data: dict, db: Session = Depends(get_db)):
    # 极简 Auth 逻辑
    user = db.query(db_mod.User).filter(db_mod.User.username == user_data.get("username")).first()
    if not user or user.hashed_password != user_data.get("password"): # 实际应使用 hash 对比
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"token": "mock_token", "role": user.role, "username": user.username}

@app.post("/detect")
async def detect_disease(file: UploadFile = File(...), db: Session = Depends(get_db)):
    save_dir = "static/uploads"
    os.makedirs(save_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"{save_dir}/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    results = model(file_path)
    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "box": box.xyxy.tolist()[0]
            })
    
    main_disease = detections[0]["class"] if detections else "Unknown"
    confidence = detections[0]["confidence"] if detections else 0.0
    
    # Matching Encyclopedia
    info = db.query(db_mod.Encyclopedia).filter(db_mod.Encyclopedia.disease_name.contains(main_disease)).first()
    
    # Save to history
    new_record = db_mod.DetectionRecord(
        image_path=file_path,
        disease_name=main_disease,
        confidence=confidence,
        crop_type="Unknown" # Default
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

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    records = db.query(db_mod.DetectionRecord).order_by(db_mod.DetectionRecord.timestamp.desc()).limit(10).all()
    return records

@app.get("/encyclopedia")
async def get_ency(db: Session = Depends(get_db)):
    return db.query(db_mod.Encyclopedia).all()

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    # 统计 Top 5 病害
    from sqlalchemy import func
    stats = db.query(db_mod.DetectionRecord.disease_name, func.count(db_mod.DetectionRecord.id).label('total'))\
              .group_by(db_mod.DetectionRecord.disease_name)\
              .order_by(func.count(db_mod.DetectionRecord.id).desc()).limit(5).all()
    return [{"name": s[0], "value": s[1]} for s in stats]

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
