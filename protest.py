import json
import os
import random

PROTEST_FILE          = "data/protest.json"
PROTEST_THRESHOLD     = 200.0
PROTEST_DURATION      = 300.0
PROTEST_CHECK_INTERVAL = 60.0
PROTEST_BASE_CHANCE   = 0.12
PROTEST_MAX_CHANCE    = 0.80


class ProtestManager:
    def __init__(self):
        self.active       = False
        self.timer        = 0.0
        self.check_timer  = 0.0
        self._load()

    def _load(self):
        try:
            if os.path.exists(PROTEST_FILE):
                with open(PROTEST_FILE) as f:
                    d = json.load(f)
                self.active      = bool(d.get("active", False))
                self.timer       = float(d.get("timer", 0.0))
                self.check_timer = float(d.get("check_timer", 0.0))
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(PROTEST_FILE, "w") as f:
            json.dump({
                "active":      self.active,
                "timer":       self.timer,
                "check_timer": self.check_timer,
            }, f)

    def tick(self, dt, pollution):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
                self.timer  = 0.0
                return "dispersed"
        else:
            if pollution >= PROTEST_THRESHOLD:
                self.check_timer += dt
                if self.check_timer >= PROTEST_CHECK_INTERVAL:
                    self.check_timer = 0.0
                    excess = (pollution - PROTEST_THRESHOLD) / PROTEST_THRESHOLD
                    chance = min(PROTEST_MAX_CHANCE, PROTEST_BASE_CHANCE + excess * 0.35)
                    if random.random() < chance:
                        self._start()
                        return "started"
            else:
                self.check_timer = 0.0
        return None

    def _start(self):
        self.active = True
        self.timer  = PROTEST_DURATION

    def is_blocking(self):
        return self.active

    def get_remaining(self):
        return max(0.0, self.timer)

    def get_remaining_str(self):
        rem = self.get_remaining()
        return f"{int(rem) // 60}:{int(rem) % 60:02d}"
