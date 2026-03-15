from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    role: str
    token: str

class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    box: List[float]

class DetectionResponse(BaseModel):
    status: str
    image_url: str
    detections: List[DetectionResult]
    main_disease: str
    cause: str
    treatment: str

class HistoryRecord(BaseModel):
    id: int
    image_path: str
    disease_name: str
    confidence: float
    timestamp: datetime
    crop_type: Optional[str]

    class Config:
        from_attributes = True

class EncyclopediaItem(BaseModel):
    disease_name: str
    crop_type: str
    cause: str
    treatment: str
    description: str

    class Config:
        from_attributes = True
