"""Train the emergency-vehicle detector. Put a YOLO-format dataset in data/ (see README)."""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(data="data/data.yaml", epochs=50, imgsz=640, batch=16)
# best weights -> runs/detect/train/weights/best.pt ; copy to models/emergency.pt
