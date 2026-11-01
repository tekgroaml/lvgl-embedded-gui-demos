"""Deterministic, linked showroom simulations, not hardware or flight models."""
from dataclasses import dataclass
import math


def smooth(value):
    value=max(0.,min(1.,value))
    return value*value*(3-2*value)


@dataclass
class FlightData:
    airspeed_kt: float = 108.
    altitude_ft: float = 2000.
    vertical_speed_fpm: float = 0.
    pitch_deg: float = 2.
    bank_deg: float = 0.
    heading_deg: float = 90.
    phase: str = 'CLIMB'
    elapsed_s: float = 0.
    stale: bool = False
    simulated: bool = True


class FlightDemo:
    """Six-minute airborne cycle, with altitude derivative and coordinated turns."""
    path=None
    PERIOD=360.

    def read(self,elapsed):
        if not math.isfinite(elapsed) or elapsed<0:raise ValueError('Invalid elapsed time')
        t=elapsed%self.PERIOD
        if t<100:
            u=t/100;phase='CLIMB';height=2000+1200*smooth(u)
            vsi=1200*6*u*(1-u)/100*60
            speed=108+14*smooth(u)
        elif t<180:
            u=(t-100)/80;phase='CRUISE';height=3200.;vsi=0.;speed=122+10*smooth(u)
        elif t<280:
            u=(t-180)/100;phase='DESCENT';height=3200-1200*smooth(u)
            vsi=-1200*6*u*(1-u)/100*60
            speed=132-16*smooth(u)
        else:
            u=(t-280)/80;phase='LEVEL';height=2000.;vsi=0.;speed=116-8*smooth(u)
        # d(altitude)/dt equals VSI; pitch includes a small trim angle.
        pitch=2+math.degrees(math.atan2(vsi/60,speed*1.68781))
        omega=2*math.pi/180
        heading=90+70*math.sin(omega*t)
        heading_rate=math.radians(70*omega*math.cos(omega*t))
        bank=math.degrees(math.atan(speed*.514444*heading_rate/9.80665))
        return FlightData(speed,height,vsi,pitch,bank,heading,phase,elapsed)


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
        if not math.isfinite(elapsed) or elapsed<0:raise ValueError('Invalid elapsed time')
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


def make_scene(view):
    """Return independent panel components and the explicit demo data source."""
    if view=='flight':
        from .flight_panels import AttitudePanel,AirDataPanel
        return (AttitudePanel(),AirDataPanel()),FlightDemo()
    if view=='industrial':
        from .process_panels import PumpPanel,ProcessTrends
        return (PumpPanel(),ProcessTrends()),ProcessDemo()
    if view=='automotive-industrial':
        from .automotive_gauge import AutomotiveGauge
        from .industrial_panel import IndustrialPanel
        from .common import TelemetrySource
        return (AutomotiveGauge(),IndustrialPanel()),TelemetrySource()
    raise ValueError('Unknown view')
