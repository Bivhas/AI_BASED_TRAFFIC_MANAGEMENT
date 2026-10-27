"""Adaptive 4-way signal controller with emergency-vehicle preemption."""
LANES = ("N", "E", "S", "W")


class SignalController:
    def __init__(self, lanes=LANES, mode="smart", min_green=8, max_green=40,
                 per_vehicle=1.5, fixed_green=20, yellow=3, emergency_hold=8):
        self.lanes, self.mode = lanes, mode
        self.min_green, self.max_green = min_green, max_green
        self.per_vehicle, self.fixed_green = per_vehicle, fixed_green
        self.yellow, self.emergency_hold = yellow, emergency_hold
        self.idx, self.phase, self.target = 0, "GREEN", None
        self.timer = fixed_green if mode == "fixed" else min_green

    @property
    def current(self):
        return self.lanes[self.idx]

    def _green_time(self, count):
        if self.mode == "fixed":
            return self.fixed_green
        return min(self.max_green, self.min_green + self.per_vehicle * count)

    def _pick_next(self, counts):
        others = [l for l in self.lanes if l != self.current]
        if self.mode == "fixed":  # plain round-robin
            return self.lanes[(self.idx + 1) % len(self.lanes)]
        return max(others, key=lambda l: counts.get(l, 0))  # busiest lane

    def update(self, counts, emergencies=(), dt=1.0):
        """counts: {lane: n_vehicles}; emergencies: lanes with an emergency vehicle."""
        self.timer -= dt
        if self.mode == "smart" and emergencies:
            lane = self.current if self.current in emergencies else \
                next(l for l in self.lanes if l in emergencies)
            if lane == self.current and self.phase == "GREEN":
                self.timer = max(self.timer, self.emergency_hold)  # hold green
            elif self.phase == "GREEN":                            # preempt
                self.phase, self.timer, self.target = "YELLOW", self.yellow, lane
            else:
                self.target = lane
        if self.timer <= 0:
            if self.phase == "GREEN":
                self.phase, self.timer = "YELLOW", self.yellow
                self.target = self._pick_next(counts)
            else:
                self.idx = self.lanes.index(self.target)
                self.phase, self.target = "GREEN", None
                self.timer = self._green_time(counts.get(self.current, 0))
                if emergencies and self.current in emergencies:
                    self.timer = max(self.timer, self.emergency_hold)
        return self.states()

    def states(self):
        return {l: (self.phase if l == self.current else "RED") for l in self.lanes}
