import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import User, DiseaseEncyclopedia
from app.core.security import get_password_hash

def init():
    print("--- Start Initializing Database ---")
    
    # 确保表结构最新
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. 创建管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@agri.com",
                hashed_password=get_password_hash("123456"),
                role="admin"
            )
            db.add(admin)
            print("Admin account created: admin / 123456")
        else:
            print("Admin already exists.")

        # 2. 录入数据
        encyclopedia_data = [
            {"name": "苹果黑腐病", "crop_type": "Apple", "causes": "真菌侵染", "prevention": "喷洒药剂"},
            {"name": "葡萄黑腐病", "crop_type": "Grape", "causes": "高温高湿", "prevention": "通风排水"},
            {"name": "苹果黑星病", "crop_type": "Apple", "causes": "叶片受损", "prevention": "深翻土壤"}
        ]

        for item in encyclopedia_data:
            if not db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.name == item["name"]).first():
                entry = DiseaseEncyclopedia(**item)
                db.add(entry)
                print(f"Data imported: {item['name']}")

        db.commit()
        print("--- Initialization Complete ---")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init()
