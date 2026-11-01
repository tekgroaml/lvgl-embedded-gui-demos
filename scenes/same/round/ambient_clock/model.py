"""Demonstration clock/weather; no network, real location or weather data."""
from dataclasses import dataclass
from common.simulation import validate_elapsed


@dataclass
class ClockData:
    elapsed_s: float
    hour: int
    minute: int
    second: float
    date_label: str = 'SUNDAY / NOV 01'
    temperature_c: int = 26
    humidity_pct: int = 61
    weather: str = 'SUNNY'
    stale: bool = False
    simulated: bool = True


def sample(elapsed):
    validate_elapsed(elapsed)
    seconds=(12*3600+30*60+elapsed)%86400
    return ClockData(elapsed,int(seconds//3600),int(seconds//60)%60,seconds%60)


class ClockDemo:
    path=None
    def read(self,elapsed):return sample(elapsed)
