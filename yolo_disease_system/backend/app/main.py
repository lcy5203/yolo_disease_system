from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import auth, detection, history
from app.core.config import settings
from app.db.session import engine
from app.models.models import Base, Encyclopedia, User, SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

# Seed Data (Quick Version)
def seed_db():
    db = SessionLocal()
    if db.query(User).count() == 0:
        db.add(User(username="admin", hashed_password="password", role="admin"))
    if db.query(Encyclopedia).count() == 0:
        db.add(Encyclopedia(
            disease_name="Tomato Early Blight", 
            crop_type="Tomato", 
            cause="Fungus infection", 
            treatment="Apply fungicide", 
            description="Small brown spots on leaves"
        ))
    db.commit()
    db.close()

seed_db()

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(detection.router, prefix="/api/detection", tags=["detection"])
app.include_router(history.router, prefix="/api/info", tags=["info"])

@app.get("/")
async def root():
    return {"message": "Welcome to YOLO Disease Detection API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
