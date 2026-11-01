"""Original mixed demo and backward-compatible optional JSON source."""
import math
from common.telemetry import Telemetry, JsonTelemetrySource


class TelemetrySource(JsonTelemetrySource):
    def __init__(self,path=None):
        if path is not None:
            super().__init__(path)
        else:
            self.path=None

    def read(self,elapsed):
        if self.path is None:
            speed = 98 + 75*math.sin(elapsed*.25 - 1)
            rpm = 950 + speed*29 + 1050*(.5+.5*math.sin(elapsed*.47))
            return Telemetry(speed, rpm, 76+23*math.sin(elapsed*.12),
                             4.2+math.sin(elapsed*.7)*.8, 13.7+.3*math.sin(elapsed),
                             .7*math.sin(elapsed*5)+.12*math.sin(elapsed*17))
        return super().read(elapsed)
