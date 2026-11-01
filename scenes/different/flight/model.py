"""Linked airborne demonstration data; no external flight simulation input."""
from dataclasses import dataclass
import math
from common.simulation import smooth, validate_elapsed

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
        validate_elapsed(elapsed)
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
