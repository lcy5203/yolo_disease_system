from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user") # 'user' or 'admin'

class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_image = Column(String)
    result_image = Column(String)
    disease_name = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DiseaseEncyclopedia(Base):
    __tablename__ = "disease_encyclopedia"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    crop_type = Column(String)
    causes = Column(Text)
    prevention = Column(Text)
    image_url = Column(String)
