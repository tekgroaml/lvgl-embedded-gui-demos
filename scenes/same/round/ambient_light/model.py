"""Smooth deterministic lighting changes; no physical LED/brightness control."""
from dataclasses import dataclass
import math
from common.simulation import validate_elapsed


@dataclass
class LightData:
    elapsed_s: float
    hue: float
    brightness: float
    rotation: float
    mood: str = 'CYBER GLOW'
    stale: bool = False
    simulated: bool = True


def sample(elapsed):
    validate_elapsed(elapsed)
    breath=.5-.5*math.cos(math.tau*elapsed/7)
    return LightData(elapsed,(.84+elapsed/24)%1,70+25*breath,elapsed*20)


class LightDemo:
    path=None
    def read(self,elapsed):return sample(elapsed)
