"""Pump-station duty cycle and pressure/thermal response."""
from dataclasses import dataclass
import math
from common.simulation import smooth, validate_elapsed

@dataclass
class ProcessData:
    rpm: float = 0.
    load_percent: float = 0.
    pressure_bar: float = 1.1
    flow_lmin: float = 0.
    temperature_c: float = 30.
    vibration_mm_s: float = .2
    power_kw: float = 0.
    produced_liters: float = 0.
    phase: str = 'STANDBY'
    elapsed_s: float = 0.
    stale: bool = False
    simulated: bool = True


def process_demand(elapsed):
    t=elapsed%120
    if t<12:return 0.,'STANDBY'
    if t<30:return .85*smooth((t-12)/18),'SOFT START'
    if t<75:return .85+.07*math.sin(math.pi*(t-30)/45)**2,'RUNNING'
    if t<90:return .85*(1-smooth((t-75)/15)),'UNLOADING'
    return 0.,'COOL DOWN'


class ProcessDemo:
    """A two-minute pump duty cycle with pressure/thermal inertia and real totals."""
    path=None

    def __init__(self):
        self.last_time=0.
        self.rpm=0.
        self.pressure=1.1
        self.temperature=30.
        self.total=0.

    @staticmethod
    def flow(rpm,pressure):
        return max(0.,(rpm/3000)*66-(pressure-1.1)*1.5)

    def read(self,elapsed):
        validate_elapsed(elapsed)
        if elapsed<self.last_time:self.__init__()
        # Normal runtime advances at 5 Hz. Integrate on a fixed small step so
        # animation FPS and polling frequency do not change the machine response.
        while self.last_time<elapsed-1e-9:
            dt=min(.05,elapsed-self.last_time)
            now=self.last_time+dt
            demand,_=process_demand(now)
            self.rpm+=(3000*demand-self.rpm)*(1-math.exp(-dt/1.5))
            self.pressure+=(1.1+5.5*demand-self.pressure)*(1-math.exp(-dt/3))
            self.temperature+=(30+35*demand-self.temperature)*(1-math.exp(-dt/25))
            self.total+=self.flow(self.rpm,self.pressure)*dt/60
            self.last_time=now
        demand,phase=process_demand(elapsed)
        ratio=self.rpm/3000
        vibration=.2+.7*ratio**2+.35*demand+.04*ratio*math.sin(7*elapsed)
        power=18.5*ratio*(.25+.75*demand)
        return ProcessData(self.rpm,demand*100,self.pressure,self.flow(self.rpm,self.pressure),
                           self.temperature,vibration,power,self.total,phase,elapsed)
