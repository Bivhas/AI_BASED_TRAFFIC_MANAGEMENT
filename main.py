"""Run the full pipeline on 4 video feeds (one per approach lane).

python main.py --videos north.mp4 east.mp4 south.mp4 west.mp4 --weights models/emergency.pt
"""
import argparse
import cv2
from detector import TrafficDetector, EMERGENCY
from controller import SignalController, LANES

COLORS = {"GREEN": (0, 200, 0), "YELLOW": (0, 200, 255), "RED": (0, 0, 220)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", nargs=4, required=True, help="N E S W sources (file or camera id)")
    ap.add_argument("--weights", default="models/emergency.pt")
    a = ap.parse_args()

    det = TrafficDetector(a.weights)
    caps = {l: cv2.VideoCapture(int(v) if v.isdigit() else v) for l, v in zip(LANES, a.videos)}
    ctrl = SignalController()
    counts, emerg = {l: 0 for l in LANES}, set()
    states, frame_i = ctrl.states(), 0

    while True:
        frames = {}
        for l, cap in caps.items():
            ok, f = cap.read()
            if not ok:
                return
            frames[l] = f
        if frame_i % 5 == 0:  # detect every 5th frame to save compute
            emerg = set()
            for l, f in frames.items():
                dets = det.detect(f)
                counts[l], has_e = det.summarize(dets)
                if has_e:
                    emerg.add(l)
                frames[l] = f.copy()
                for n, c, (x1, y1, x2, y2) in dets:
                    col = (0, 0, 255) if n in EMERGENCY else (255, 200, 0)
                    cv2.rectangle(frames[l], (x1, y1), (x2, y2), col, 2)
                    cv2.putText(frames[l], f"{n} {c:.2f}", (x1, y1 - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
        if frame_i % 25 == 0:  # controller tick ~1 s at 25 fps
            states = ctrl.update(counts, emerg)
        for l, f in frames.items():
            cv2.putText(f, f"{l}: {states[l]}  cars={counts[l]}" + ("  EMERGENCY" if l in emerg else ""),
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS[states[l]], 2)
            cv2.imshow(l, cv2.resize(f, (480, 320)))
        frame_i += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    main()
