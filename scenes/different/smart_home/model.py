"""Deterministic home simulation with explicit solar/load/grid energy balance."""
from dataclasses import dataclass
import math
from common.simulation import validate_elapsed


@dataclass
class HomeData:
    temperature_c: float
    humidity_pct: float
    target_c: float
    light_pct: float
    hvac: str
    solar_w: float
    house_w: float
    grid_w: float
    hvac_w: float
    elapsed_s: float
    stale: bool = False
    simulated: bool = True


class HomeDemo:
    path=None

    def read(self,elapsed):
        validate_elapsed(elapsed)
        t=elapsed
        temperature=22.5+.8*math.sin(t/14)
        cooling=temperature>22.5
        hvac_w=420+280*abs(math.sin(t/14))
        light=60+25*math.sin(t/7)
        solar=1400+650*math.sin(t/9)
        house=620+light*2+hvac_w+130*math.sin(t/6)
        return HomeData(temperature,47+5*math.sin(t/18),22.5,light,
                        'COOLING' if cooling else 'HEATING',solar,house,house-solar,hvac_w,t)
