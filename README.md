# Smart Traffic System with AI-Based Emergency Vehicle Detection

## 1. Problem
Fixed-time signals ignore real traffic and make ambulances/fire trucks wait at red lights.
This project (a) measures traffic density per lane with computer vision and (b) detects
emergency vehicles so the junction gives them a green path automatically.

## 2. Architecture
Camera per lane -> YOLOv8 detector -> (vehicle count, emergency flag) -> Signal controller -> Lights

| File | Role |
|---|---|
| `detector.py` | YOLO inference; counts vehicles, flags ambulance / fire_truck / police_car |
| `controller.py` | Adaptive green time (min 8 s + 1.5 s/vehicle, max 40 s), busiest-lane-next, emergency preemption (yellow -> green, held while vehicle visible) |
| `main.py` | Live/video pipeline with overlay |
| `simulate.py` | Fixed-time vs. smart comparison, no GPU/video needed |
| `train.py` | Fine-tunes YOLO on an emergency-vehicle dataset |

## 3. Setup
    pip install -r requirements.txt
    python simulate.py                      # works immediately
    python main.py --videos n.mp4 e.mp4 s.mp4 w.mp4

## 4. Training the emergency detector
Stock COCO YOLO has no ambulance class, so fine-tune it:
1. Download a YOLO-format dataset (Roboflow Universe: search "ambulance fire truck detection"; Kaggle also has several).
2. Use classes: `car, motorcycle, bus, truck, ambulance, fire_truck, police_car`.
3. Place it in `data/` with `data.yaml`, run `python train.py`, copy `best.pt` to `models/emergency.pt`.
4. Report mAP@0.5, precision/recall per class (especially ambulance recall).

## 5. Control logic
- Green time scales with queue length (adaptive).
- Next green goes to the lane with most vehicles.
- Emergency in a red lane: current green -> yellow (3 s safety) -> green for that lane.
- Emergency in the green lane: green is held until it leaves.

## 6. Evaluation
`simulate.py` reports average wait and emergency-vehicle wait for both strategies (1-hour, seeded).
For the real model, evaluate detection with mAP and the end-to-end system on recorded junction video.

## 7. Limitations & future work
- Vision alone struggles at night/rain/occlusion -> add **siren audio detection** (microphone + CNN on mel-spectrograms) and fuse with vision.
- Multiple simultaneous emergencies need a priority queue.
- Real deployment requires a certified controller/fail-safe (all-red fallback) and V2I (e.g. DSRC/5G) for earlier warning.
- Add license-free edge hardware (Jetson / Raspberry Pi + Coral) benchmarks.
