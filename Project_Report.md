# Smart Traffic System Using AI with Emergency Vehicle Detection

*Project Report*

## Abstract

Urban junctions that rely on fixed-time traffic signals waste time on empty lanes and force emergency vehicles to wait in the same queues as everyone else. This project presents a smart traffic system that combines computer vision with an adaptive signal controller. A YOLO object detector, run on camera feeds from each approach, counts vehicles per lane and flags the presence of emergency vehicles (ambulance, fire truck, police car). A rule-based controller uses these inputs to adjust green times to the real traffic density and to preempt the signal in favour of an emergency vehicle. A simulation of a four-way junction over one hour, using identical random traffic for both strategies, showed that the smart controller reduced the average vehicle wait from 49.8 s to 33.6 s (about 32% lower) and the average emergency-vehicle wait from 28.1 s to 2.2 s (about 92% lower). The complete software, including the detector, controller, video pipeline, simulator and training script, is implemented in Python.

## 1. Introduction

Traffic congestion increases travel time, fuel consumption, emissions and driver stress. A major cause at signalised junctions is that conventional controllers run a pre-set cycle: each approach receives the same green time whether it holds two vehicles or thirty. When a lane is empty, its green phase is wasted while other lanes build long queues.

The problem is more serious for emergency services. An ambulance carrying a patient, or a fire engine heading to an incident, loses critical minutes when it reaches a red signal and has to wait behind queued vehicles. Manual intervention by traffic police is not possible at every junction.

Advances in deep learning, particularly real-time object detection, make it practical to understand a traffic scene from an ordinary camera. This project uses that capability to build a junction controller that reacts to what is actually happening on the road.

## 2. Problem Statement

To design and implement a traffic signal system that (a) estimates traffic density in each lane using computer vision, (b) allocates green time according to demand, and (c) automatically detects approaching emergency vehicles and gives them a clear passage with minimal delay to other traffic.

## 3. Objectives

- Detect and count vehicles in each lane from video using a deep-learning detector.
- Detect emergency vehicles (ambulance, fire truck, police car) in real time.
- Implement an adaptive signal controller that responds to queue length.
- Implement emergency preemption with a safety yellow phase.
- Evaluate the system against a conventional fixed-time controller.

## 4. Background and Related Approaches

**Fixed-time control** uses a constant cycle and is simple and cheap, but it cannot respond to changing demand.

**Actuated control** uses inductive loops or sensors embedded in the road. It reacts to vehicle presence but needs costly installation and maintenance, and it gives little information about the type of vehicle.

**Vision-based control** uses cameras and image processing. Cameras are already common at junctions, can be added without digging up the road, and can distinguish vehicle types, which is what makes emergency-vehicle detection possible.

**Object detection with YOLO.** YOLO (You Only Look Once) frames detection as a single neural-network pass that predicts bounding boxes and class labels together, giving real-time speed suitable for live video (Redmon et al., 2016). This project uses the YOLOv8 implementation from Ultralytics.

**Other emergency-vehicle cues.** Emergency vehicles can also be identified by siren sound, vehicle-to-infrastructure (V2I) radio messages or GPS-based preemption. These are discussed under future work.

## 5. System Architecture

The system consists of four stages arranged as a pipeline.

1. **Sensing:** one camera per approach (North, East, South, West).
2. **Perception:** a YOLO model processes frames and outputs labelled bounding boxes. A summary step converts them into two values per lane: the vehicle count and an emergency flag.
3. **Decision:** the signal controller takes the counts and flags and decides which lane is green and for how long.
4. **Actuation and display:** the signal states are applied, and an on-screen overlay shows detections, counts and signal colours.

| Module | File | Responsibility |
|---|---|---|
| Detector | detector.py | YOLO inference, vehicle counting, emergency flag |
| Controller | controller.py | Adaptive timing, lane selection, emergency preemption |
| Pipeline | main.py | Reads four video sources, runs detection and control, draws overlay |
| Simulator | simulate.py | Compares fixed-time and smart control without hardware |
| Training | train.py | Fine-tunes YOLO on an emergency-vehicle dataset |

## 6. Methodology

### 6.1 Vehicle and emergency-vehicle detection

The detector is a YOLOv8 model. The standard COCO-trained weights recognise cars, buses, trucks and motorcycles but have no ambulance or fire-truck class. The model is therefore fine-tuned on a labelled dataset containing the classes: car, motorcycle, bus, truck, ambulance, fire_truck and police_car. The last three form the emergency set.

For every processed frame the detector returns a list of (class, confidence, bounding box). A confidence threshold of 0.4 is used to discard weak detections. The summary step then computes:

- **count:** the number of detections belonging to any vehicle class;
- **emergency flag:** true if at least one detection belongs to the emergency set.

To reduce computation, detection runs on every fifth frame, since traffic changes slowly compared with the frame rate.

### 6.2 Dataset and training

A YOLO-format dataset of road scenes with emergency vehicles is used (for example, one of the public sets available on Roboflow Universe or Kaggle). Training starts from the pretrained yolov8n weights and runs for 50 epochs at 640 px image size with batch size 16. Standard augmentation (flip, scale, colour jitter) is applied by the framework. The best checkpoint is saved as models/emergency.pt.

### 6.3 Signal control algorithm

The controller manages a four-way junction in which exactly one lane is green at a time and all others are red.

**Adaptive green time.** When a lane receives green, its duration is

*green = min(40, 8 + 1.5 x n)*

where n is the number of vehicles currently counted in that lane. The minimum of 8 s prevents very short, unsafe phases, and the 40 s maximum prevents one lane from starving the others.

**Next-lane selection.** When a green phase ends, the signal passes through a 3 s yellow phase and then gives green to the lane with the highest vehicle count among the others.

**Emergency preemption.**

- If an emergency vehicle is detected in a red lane, the current green phase is cut short, a 3 s yellow phase is shown, and the emergency lane then receives green.
- If the emergency vehicle is in the lane that is already green, the green is held (at least 8 s remaining) for as long as the vehicle remains visible.
- Once no emergency vehicle is detected, normal adaptive operation resumes.

The yellow phase before switching preserves safety for vehicles already in the junction.

**Baseline.** For comparison, a fixed-time mode gives each lane 20 s of green in round-robin order with a 3 s yellow, ignoring counts and emergencies.

## 7. Implementation

The system is written in Python. The libraries used are Ultralytics (YOLOv8), OpenCV (video input and overlay) and NumPy. The command python main.py with four video sources runs the full pipeline: frames from each lane are read, detections are drawn as boxes (red for emergency vehicles, blue for others), and each window shows the lane's signal state, vehicle count and an EMERGENCY label when applicable. The controller is updated about once per second of video.

The controller is deliberately separated from the detector. It only needs two inputs per lane (count and emergency flag), so it can be tested, replaced or reused with any other sensing method.

## 8. Simulation and Results

### 8.1 Simulation setup

To evaluate the control logic independently of video data, a discrete-time simulator models the junction with one-second steps over 3600 s (one hour). The same random seed is used for both strategies, so both face identical traffic.

| Parameter | Value |
|---|---|
| Arrival rate, North and South | 0.20 vehicles/s each |
| Arrival rate, East and West | 0.06 vehicles/s each |
| Discharge rate on green | 1 vehicle/s |
| Emergency vehicle arrival | probability 1/180 per second, random lane |
| Fixed-time green / yellow | 20 s / 3 s |
| Smart controller green range | 8 to 40 s (8 + 1.5 per vehicle) |

The unequal demand deliberately creates a main road (North-South) and a side road (East-West), which is typical of real junctions and shows the benefit of adaptivity. An emergency vehicle waits from its arrival until its lane turns green and then clears immediately, on the assumption that queued vehicles yield.

### 8.2 Results

| Metric | Fixed-time | Smart controller | Improvement |
|---|---|---|---|
| Average vehicle wait | 49.8 s | 33.6 s | about 32% lower |
| Average emergency-vehicle wait | 28.1 s | 2.2 s | about 92% lower |
| Longest emergency-vehicle wait | 70 s | 3 s | about 96% lower |
| Emergency vehicles served | 19 | 20 | - |

The slightly different number of emergency vehicles served reflects only the vehicles that had been cleared by the end of the hour.

### 8.3 Detection results

Detection metrics depend on the dataset used for training and must be measured on a held-out test set once the model is trained. The following table is to be completed with the measured values.

| Class | Precision | Recall | mAP@0.5 |
|---|---|---|---|
| Car | to be measured | to be measured | to be measured |
| Bus / Truck | to be measured | to be measured | to be measured |
| Ambulance | to be measured | to be measured | to be measured |
| Fire truck | to be measured | to be measured | to be measured |
| Police car | to be measured | to be measured | to be measured |

Recall on emergency classes is the most important figure, because a missed ambulance means no preemption.

## 9. Discussion

The simulation shows two separate benefits. First, adaptive timing lowers the average wait for all vehicles because green time moves to the lanes that need it. Second, preemption nearly eliminates emergency-vehicle delay; the remaining 2 to 3 seconds is the unavoidable yellow phase that keeps the junction safe.

**Limitations.**

- The results come from a simplified simulation with assumed demand, not from a real junction. Absolute numbers will differ in practice.
- Camera-based detection degrades at night, in heavy rain or fog, and when a large vehicle hides an emergency vehicle.
- A false positive would give an unnecessary green to one lane, and a missed detection gives no preemption. A real deployment should be tuned using the measured precision and recall.
- The emergency vehicle is detected only once it is in the camera view, which limits how early the signal can react.
- Only one emergency vehicle is handled at a time. Simultaneous emergencies in different lanes need a priority rule.
- Pedestrian phases and turning movements are not modelled.

## 10. Future Work

- **Siren audio detection:** add a microphone and a CNN on mel-spectrograms, and fuse the audio result with vision to improve detection at night and in poor visibility.
- **Earlier warning:** use V2I communication or GPS preemption so the signal can react before the vehicle is visible.
- **Multi-junction coordination:** create a green corridor across consecutive junctions along the emergency route.
- **Learning-based control:** replace the rule-based controller with reinforcement learning trained in simulation.
- **Edge deployment:** run the detector on an embedded device such as an NVIDIA Jetson and measure latency and power use.
- **Fail-safe design:** add a hardware watchdog so the junction falls back to a safe fixed plan if the AI system fails.
- **Validation in a traffic simulator** such as SUMO and on recorded real-junction video.

## 11. Conclusion

This project demonstrates a smart traffic system that senses traffic with cameras, counts vehicles and recognises emergency vehicles using a YOLO detector, and controls signals adaptively with emergency preemption. In simulation it reduced average waiting time by about a third and cut emergency-vehicle delay from roughly 28 s to about 2 s. The modular design allows the detector, controller and sensing method to be improved independently. With a trained emergency-vehicle model and validation on real footage, the approach offers a low-cost way to make junctions more efficient and to give emergency services faster passage.

## References

1. J. Redmon, S. Divvala, R. Girshick and A. Farhadi, "You Only Look Once: Unified, Real-Time Object Detection," IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.
2. Ultralytics, "YOLOv8 Documentation," docs.ultralytics.com.
3. G. Bradski, "The OpenCV Library," Dr. Dobb's Journal of Software Tools, 2000.
4. Roboflow Universe, public ambulance and emergency-vehicle detection datasets, universe.roboflow.com.
