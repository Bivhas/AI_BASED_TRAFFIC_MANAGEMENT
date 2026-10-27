"""Compare fixed-time vs. smart (adaptive + emergency preemption) control."""
import random
from controller import SignalController, LANES

DEMAND = {"N": 0.20, "S": 0.20, "E": 0.06, "W": 0.06}  # arrivals / second


def run(mode, seconds=3600, seed=7, emergency_rate=1 / 180):
    rng = random.Random(seed)
    ctrl = SignalController(mode=mode)
    queue = {l: [] for l in LANES}      # arrival times of normal vehicles
    emerg = {l: [] for l in LANES}      # arrival times of emergency vehicles
    waits, ewaits = [], []
    states = ctrl.states()
    for t in range(seconds):
        for l in LANES:
            if rng.random() < DEMAND[l]:
                queue[l].append(t)
        if rng.random() < emergency_rate:
            emerg[rng.choice(LANES)].append(t)
        counts = {l: len(queue[l]) for l in LANES}
        active = {l for l in LANES if emerg[l]}
        states = ctrl.update(counts, active)
        for l in LANES:
            if states[l] == "GREEN":
                if queue[l]:
                    waits.append(t - queue[l].pop(0))   # 1 vehicle / second
                while emerg[l]:
                    ewaits.append(t - emerg[l].pop(0))
    avg = lambda x: sum(x) / len(x) if x else 0
    return avg(waits), avg(ewaits), max(ewaits, default=0), len(ewaits)


if __name__ == "__main__":
    print(f"{'mode':<8}{'avg wait (s)':>14}{'emerg avg (s)':>15}{'emerg max (s)':>15}{'#emerg':>8}")
    for m in ("fixed", "smart"):
        a, e, mx, n = run(m)
        print(f"{m:<8}{a:>14.1f}{e:>15.1f}{mx:>15.0f}{n:>8}")
