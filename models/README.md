# models/

| File | What it is |
|---|---|
| `yolov8n.pt` | Stock pretrained YOLOv8n (COCO). Detects car, motorcycle, bus, truck. **No ambulance / fire-truck class.** Used as a fallback so vehicle counting works out of the box. |
| `emergency.pt` | **You must add this.** Your fine-tuned model with classes `car, motorcycle, bus, truck, ambulance, fire_truck, police_car`. |

## How to get emergency.pt
1. Download a YOLO-format ambulance/fire-truck dataset (Roboflow Universe or Kaggle) into `data/` with a `data.yaml`.
2. Run `python train.py` (free GPU: Google Colab).
3. Copy `runs/detect/train/weights/best.pt` to `models/emergency.pt`.

Until `emergency.pt` exists, `main.py` prints a warning and only counts vehicles; emergency preemption stays inactive.
