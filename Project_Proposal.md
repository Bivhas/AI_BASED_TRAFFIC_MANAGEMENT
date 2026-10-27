# Project Proposal: Smart Traffic System Using AI with Emergency Vehicle Detection

*Submitted by: [Name / Team] | Supervisor: [Name] | Date: [Date]*

## 1. Summary

This project proposes a smart traffic signal system that uses cameras and artificial intelligence to manage junction traffic and to give emergency vehicles a fast, safe passage. A YOLO object detector will count vehicles in each lane and recognise ambulances, fire trucks and police cars. A controller will use this information to adjust green times to real demand and to switch the signal in favour of an approaching emergency vehicle. A working prototype of the controller and a simulator already exist, and the proposed work covers training the detector, integrating the full pipeline, and testing it on real traffic footage.

## 2. Background and Problem

Most junctions use fixed-time signals. Each approach gets the same green time regardless of how many vehicles are waiting, so empty lanes keep their green while busy lanes build queues. Emergency vehicles suffer most: an ambulance or fire engine that reaches a red light must wait in the queue, and the delay can affect patient outcomes and the damage caused by fires.

Sensor-based systems such as road loops are expensive to install and cannot tell an ambulance from a car. Cameras are already present at many junctions and, combined with deep-learning object detection, can provide both traffic density and vehicle type at low additional cost.

## 3. Aim and Objectives

**Aim:** to reduce waiting time at signalised junctions, and especially emergency-vehicle delay, using AI-based vision.

**Objectives**

- Train a YOLO model that detects cars, buses, trucks, motorcycles, ambulances, fire trucks and police cars.
- Estimate the number of vehicles in each lane in real time.
- Implement an adaptive signal controller with emergency preemption and a safety yellow phase.
- Compare the system with fixed-time control in simulation and on recorded junction video.
- Document the work in a final report and demonstration.

## 4. Scope

**In scope:** a four-way junction with one camera per approach; vehicle and emergency-vehicle detection; adaptive timing; preemption for one emergency vehicle at a time; simulation and video-based evaluation.

**Out of scope:** physical installation at a real junction, pedestrian phases, turning-movement control, multi-junction coordination, and integration with real signal hardware. These are listed as future work.

## 5. Proposed Methodology

1. **Data collection:** gather a public labelled dataset of emergency vehicles (for example from Roboflow Universe or Kaggle) and add locally recorded road footage if available.
2. **Model training:** fine-tune YOLOv8 from pretrained weights, evaluate with precision, recall and mAP@0.5 on a held-out test set, and focus on recall for emergency classes.
3. **Controller design:** green time = min(40, 8 + 1.5 x vehicles in lane); the next green goes to the busiest lane; an emergency vehicle in a red lane triggers a 3 s yellow phase followed by green for that lane, held until the vehicle clears.
4. **Integration:** connect detector and controller in a live pipeline with an on-screen display of detections, counts and signal states.
5. **Evaluation:** run a simulation of a four-way junction and test on recorded video; compare average vehicle wait, emergency-vehicle wait and number of detection errors against fixed-time control.

## 6. Preliminary Work and Results

The software prototype is already built in Python, with a detector module, signal controller, video pipeline, training script and simulator. In a one-hour simulation with identical random traffic for both strategies, the smart controller reduced the average vehicle wait from 49.8 s to 33.6 s and the average emergency-vehicle wait from 28.1 s to 2.2 s. These figures come from a simplified model with assumed traffic demand and need to be confirmed on real data, which is the purpose of the proposed work.

## 7. Deliverables

- Trained emergency-vehicle detection model with evaluation metrics.
- Complete source code: detector, controller, pipeline, simulator and training scripts.
- Demonstration of the live pipeline on recorded junction video.
- Comparison results of fixed-time versus smart control.
- Final project report and presentation.

## 8. Work Plan

The project is planned for 12 weeks.

| Weeks | Activity | Output |
|---|---|---|
| 1-2 | Literature review, requirements, dataset search | Dataset and project plan |
| 3-5 | Data preparation and model training | Trained detector with metrics |
| 6-7 | Controller refinement and testing in simulation | Validated control logic |
| 8-9 | Pipeline integration and video testing | Working end-to-end demo |
| 10 | Evaluation and comparison with fixed-time control | Results tables and charts |
| 11 | Report writing | Draft report |
| 12 | Final testing, presentation and submission | Final report and demo |

## 9. Resources Required

| Resource | Purpose | Estimated cost |
|---|---|---|
| Computer with a GPU (or free cloud GPU such as Google Colab) | Model training | Free to moderate |
| Public datasets | Training and testing | Free |
| Recorded junction footage or a webcam | Testing | Low |
| Software: Python, Ultralytics YOLO, OpenCV | Development | Free, open source |
| Optional: Jetson or Raspberry Pi | Edge deployment test | Moderate |

Costs are rough estimates and depend on the equipment already available.

## 10. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Too little emergency-vehicle training data | Use several public datasets and data augmentation |
| Poor detection at night or in rain | Include varied conditions in training; propose siren-audio fusion as an extension |
| Missed or false emergency detections | Tune confidence threshold using measured precision and recall; report error rates openly |
| Limited computing power | Use a small model (YOLOv8n) and free cloud GPUs |
| Lack of real junction footage | Use public traffic videos and the simulator |

## 11. Expected Outcomes and Benefits

- Shorter average waiting times through demand-based green allocation.
- Much faster passage for ambulances and fire engines, with a safe signal change.
- A low-cost approach that reuses existing cameras.
- A modular design that can later be extended with siren detection, V2I communication and multi-junction coordination.

## 12. Conclusion

The project addresses a practical problem, congestion and emergency-vehicle delay at junctions, using well-established and freely available tools. A working prototype already demonstrates the control logic, and the remaining work is focused, achievable within 12 weeks, and measurable against a clear baseline.

## References

1. J. Redmon, S. Divvala, R. Girshick and A. Farhadi, "You Only Look Once: Unified, Real-Time Object Detection," IEEE CVPR, 2016.
2. Ultralytics, "YOLOv8 Documentation," docs.ultralytics.com.
3. G. Bradski, "The OpenCV Library," Dr. Dobb's Journal of Software Tools, 2000.
