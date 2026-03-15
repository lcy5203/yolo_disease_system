from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

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
