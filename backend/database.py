from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user") # "user" or "admin"

class DetectionRecord(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    disease_name = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    crop_type = Column(String) # e.g., Tomato, Corn

class Encyclopedia(Base):
    __tablename__ = "encyclopedia"
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, unique=True)
    crop_type = Column(String)
    cause = Column(Text)
    treatment = Column(Text)
    description = Column(Text)

Base.metadata.create_all(bind=engine)

# 初始化一些数据
def init_db():
    db = SessionLocal()
    # 初始化百科
    if db.query(Encyclopedia).count() == 0:
        diseases = [
            Encyclopedia(disease_name="Tomato Early Blight", crop_type="Tomato", cause="Fungus infection", treatment="Apply fungicide", description="Small brown spots on leaves"),
            Encyclopedia(disease_name="Corn Rust", crop_type="Corn", cause="Moist weather", treatment="Ventilation", description="Yellow-orange pustules"),
            Encyclopedia(disease_name="Apple Scab", crop_type="Apple", cause="Wet spring", treatment="Pruning", description="Dark lesions on fruit/leaves")
        ]
        db.add_all(diseases)
    
    # 初始化默认管理员
    if db.query(User).count() == 0:
        default_admin = User(username="admin", hashed_password="password", role="admin") # 实际应加密
        db.add(default_admin)
        
    db.commit()
    db.close()

init_db()
