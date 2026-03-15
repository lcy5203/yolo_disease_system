from ultralytics import YOLO
import os
from app.core.config import settings

class YOLOEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        # Fallback if production model not found
        model_path = settings.MODEL_PATH
        if not os.path.exists(model_path):
            print(f"Warning: Production model not found at {model_path}. Using yolov8n.pt")
            model_path = "yolov8n.pt"
        self.model = YOLO(model_path)

    def detect(self, image_path: str):
        results = self.model(image_path)
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class": self.model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "box": box.xyxy.tolist()[0]
                })
        return detections

yolo_engine = YOLOEngine()
