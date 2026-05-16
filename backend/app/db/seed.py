# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models import DiseaseEncyclopedia, User


DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@agri.com",
    "password": "123456",
    "role": "admin",
}


DEFAULT_DISEASES = [
    {
        "name": "苹果黑星病",
        "crop_type": "Apple",
        "causes": "由苹果黑星病菌侵染引起，低温高湿、通风不良时易发生。",
        "prevention": "及时清除病叶病果，改善通风透光条件，发病初期可喷施保护性杀菌剂。",
        "image_url": "/static/figures/Apple___Apple_scab.JPG",
    },
    {
        "name": "苹果黑腐病",
        "crop_type": "Apple",
        "causes": "多由真菌侵染造成，病菌可通过伤口或弱势组织进入叶片和果实。",
        "prevention": "加强果园清洁，剪除病枝病叶，减少机械伤口，必要时使用杀菌剂防治。",
        "image_url": "/static/figures/Apple___Black_rot.JPG",
    },
    {
        "name": "苹果锈病",
        "crop_type": "Apple",
        "causes": "由锈菌侵染引起，常与雪松类寄主交替传播，高湿环境下易扩散。",
        "prevention": "减少附近转主寄主，发病季节加强巡查，及时摘除病叶并进行药剂保护。",
        "image_url": "/static/figures/Apple___Cedar_apple_rust.JPG",
    },
    {
        "name": "苹果健康叶片",
        "crop_type": "Apple",
        "causes": "叶片未表现出明显病斑或异常症状。",
        "prevention": "保持合理水肥管理和通风透光，定期巡查叶片状态，预防病害发生。",
        "image_url": "/static/figures/Apple___healthy.JPG",
    },
    {
        "name": "葡萄黑腐病",
        "crop_type": "Grape",
        "causes": "由真菌侵染引起，高温高湿、枝叶郁闭和病残体堆积会加重发病。",
        "prevention": "清除越冬病残体，改善架面通风，雨季前后加强保护性药剂防治。",
        "image_url": "/static/figures/Grape___Black_rot.JPG",
    },
    {
        "name": "葡萄黑痘病",
        "crop_type": "Grape",
        "causes": "多与真菌侵染和植株长势衰弱有关，叶片会出现褐色或黑色坏死斑。",
        "prevention": "加强肥水管理，提高植株抗性，及时剪除病叶病枝并进行针对性防治。",
        "image_url": "/static/figures/Grape___Esca_(Black_Measles).JPG",
    },
    {
        "name": "葡萄健康叶片",
        "crop_type": "Grape",
        "causes": "叶片颜色和形态正常，未检测到明显病害特征。",
        "prevention": "保持架面通风和合理修剪，注意雨季排水，定期进行病害监测。",
        "image_url": "/static/figures/Grape___healthy.JPG",
    },
    {
        "name": "葡萄叶枯病",
        "crop_type": "Grape",
        "causes": "病菌常在病残叶中越冬，次年随风雨传播，湿度大时病情发展较快。",
        "prevention": "及时清理落叶和病残体，降低田间湿度，发病初期进行药剂防治。",
        "image_url": "/static/figures/Grape___Leaf_blight_(Isariopsis_Leaf_Spot).JPG",
    },
]


def seed_defaults(db: Session) -> None:
    admin = db.query(User).filter(User.username == DEFAULT_ADMIN["username"]).first()
    if not admin:
        db.add(
            User(
                username=DEFAULT_ADMIN["username"],
                email=DEFAULT_ADMIN["email"],
                hashed_password=get_password_hash(DEFAULT_ADMIN["password"]),
                role=DEFAULT_ADMIN["role"],
            )
        )

    for item in DEFAULT_DISEASES:
        exists = db.query(DiseaseEncyclopedia).filter(DiseaseEncyclopedia.name == item["name"]).first()
        if not exists:
            db.add(DiseaseEncyclopedia(**item))
        elif not exists.image_url:
            exists.image_url = item["image_url"]

    db.commit()
