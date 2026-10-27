"""Vehicle + emergency-vehicle detection using YOLO (Ultralytics)."""
from ultralytics import YOLO

EMERGENCY = {"ambulance", "fire_truck", "police_car"}
VEHICLES = {"car", "motorcycle", "bus", "truck"} | EMERGENCY


class TrafficDetector:
    def __init__(self, weights="models/emergency.pt", conf=0.4):
        # Custom-trained weights with classes incl. ambulance/fire_truck/police_car.
        # (Stock COCO weights have no ambulance class - see README, "Training".)
        self.model = YOLO(weights)
        self.conf = conf

    def detect(self, frame):
        r = self.model.predict(frame, conf=self.conf, verbose=False)[0]
        return [(r.names[int(b.cls)], float(b.conf), tuple(map(int, b.xyxy[0])))
                for b in r.boxes]

    @staticmethod
    def summarize(dets):
        count = sum(1 for n, _, _ in dets if n in VEHICLES)
        emergency = any(n in EMERGENCY for n, _, _ in dets)
        return count, emergency
