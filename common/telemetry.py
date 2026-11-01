"""Bounded read-only JSON telemetry for the retained mixed scene."""
from dataclasses import dataclass
import json
import math
import os
import time
from .snapshots import read_snapshot

@dataclass
class Telemetry:
    speed: float = 0.0
    rpm: float = 0.0
    temperature: float = 0.0
    pressure: float = 0.0
    voltage: float = 0.0
    signal: float = 0.0
    stale: bool = False
    simulated: bool = True


class JsonTelemetrySource:
    """Read atomic JSON snapshots at up to 5 Hz, keeping last good values on failure."""
    LIMITS = {"speed": (0, 300), "rpm": (0, 9000), "temperature": (-40, 150),
              "pressure": (0, 20), "voltage": (0, 60), "signal": (-1, 1)}

    def __init__(self, path):
        if path is None:
            raise ValueError("A live JSON path is required")
        self.path = path
        self.last_poll = -1.0
        self.last = Telemetry(stale=path is not None, simulated=path is None)

    def read(self, elapsed):
        if elapsed - self.last_poll < .2: return self.last
        self.last_poll = elapsed
        try:
            values, modified = read_snapshot(self.path)
            fields = {}
            for name, (low, high) in self.LIMITS.items():
                value = values[name]
                if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
                    raise ValueError("Invalid telemetry field.")
                fields[name] = float(value)
            age = time.time() - modified
            self.last = Telemetry(**fields, stale=not -1 <= age <= 3, simulated=False)
        except (OSError, ValueError, KeyError, TypeError):
            self.last.stale = True
            self.last.simulated = False
        return self.last
