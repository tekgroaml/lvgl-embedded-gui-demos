"""A linked, deterministic urban/road driving demonstration (no OBD input)."""
from dataclasses import dataclass
import math

from common.simulation import smooth,validate_elapsed


@dataclass
class AutomotiveData:
    speed_kmh: float = 0.
    rpm: float = 850.
    gear: int = 0
    load_percent: float = 8.
    coolant_c: float = 72.
    oil_pressure_bar: float = 1.4
    fuel_percent: float = 70.
    fuel_rate_lph: float = .8
    voltage_v: float = 14.2
    trip_km: float = 0.
    phase: str = 'IDLE'
    elapsed_s: float = 0.
    stale: bool = False
    simulated: bool = True


def driving_profile(elapsed):
    """Return km/h, acceleration in km/h/s, phase; speed has smooth joins."""
    t=elapsed%180
    if t<12:return 0.,0.,'IDLE'
    if t<52:
        u=(t-12)/40
        return 100*smooth(u),100*6*u*(1-u)/40,'ACCELERATING'
    if t<102:
        u=(t-52)/50
        return 100+8*math.sin(math.pi*u)**2,8*math.pi/50*math.sin(2*math.pi*u),'CRUISING'
    if t<142:
        u=(t-102)/40
        return 100*(1-smooth(u)),-100*6*u*(1-u)/40,'BRAKING'
    return 0.,0.,'IDLE'


def drivetrain(speed,acceleration):
    if speed<.5:return 0,850.,8.
    gear=1+sum(speed>=threshold for threshold in (22,42,62,85))
    ratio=(3.6,2.2,1.52,1.12,.85)[gear-1]
    # 2m wheel circumference and 3.7 final drive. RPM falls on upshifts.
    rpm=max(850.,speed*1000/(60*2)*3.7*ratio)
    load=max(6.,min(92.,18+speed*.18+max(0,acceleration)*14))
    if acceleration<-.2:load=6.
    return gear,rpm,load


class AutomotiveDemo:
    """Three-minute road cycle; temperature/fuel/distance retain state across laps."""
    path=None
    TANK_LITERS=50.

    def __init__(self):
        self.last_time=0.
        self.coolant=72.
        self.fuel_liters=self.TANK_LITERS*.7
        self.trip_km=0.

    def read(self,elapsed):
        validate_elapsed(elapsed)
        if elapsed<self.last_time:self.__init__()
        while self.last_time<elapsed-1e-9:
            dt=min(.05,elapsed-self.last_time)
            speed,accel,_=driving_profile(self.last_time+dt)
            _,_,load=drivetrain(speed,accel)
            fuel_rate=.8+load*.10+speed*.018
            if self.fuel_liters<=0:speed=0.;fuel_rate=0.;load=0.
            self.coolant+=(76+load*.23-self.coolant)*(1-math.exp(-dt/35))
            self.fuel_liters=max(0.,self.fuel_liters-fuel_rate*dt/3600)
            self.trip_km+=speed*dt/3600
            self.last_time+=dt
        speed,accel,phase=driving_profile(elapsed)
        gear,rpm,load=drivetrain(speed,accel)
        fuel_rate=.8+load*.10+speed*.018
        voltage=14.25-.25*load/100+.04*math.sin(elapsed*.3)
        oil=max(.8,min(5.,.9+rpm*.00085-(self.coolant-72)*.008))
        if self.fuel_liters<=0:
            speed,rpm,load,gear,fuel_rate,oil,voltage=0.,0.,0.,0,0.,0.,12.4
            phase='FUEL EMPTY'
        return AutomotiveData(speed,rpm,gear,load,self.coolant,oil,
                              self.fuel_liters/self.TANK_LITERS*100,fuel_rate,voltage,
                              self.trip_km,phase,elapsed)
