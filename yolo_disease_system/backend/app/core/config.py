from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "农作物病害智能分类系统"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    UPLOAD_DIR: str = "static/uploads"
    MODEL_PATH: str = "../../models/production_v1.pt" # Adjusting path based on project root

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
