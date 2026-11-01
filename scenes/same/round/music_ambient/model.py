"""Analytic beat/envelope/palette demo. No audio files, capture or output devices."""
from dataclasses import dataclass
import colorsys
import math
from common.simulation import validate_elapsed

BPM=112
DURATION=90.
BANDS=64


@dataclass
class MusicData:
    elapsed_s: float
    title: str
    artist: str
    bpm: int
    track_seconds: float
    duration_seconds: float
    beat: float
    breath: float
    hue: float
    bands: tuple
    stale: bool = False
    simulated: bool = True


def sample(elapsed):
    validate_elapsed(elapsed)
    beats=elapsed*BPM/60
    phase=beats%1
    # Quick beat attack with a smooth release; quiet and energetic phrases
    # alternate over eight bars. Each level is a deterministic demo envelope.
    beat=math.exp(-7*phase)
    phrase=.5+.5*math.sin(math.tau*beats/32-.7)
    bands=[]
    for index in range(BANDS):
        x=index/(BANDS-1)
        low=math.exp(-((x-.12)/.19)**2)*beat
        mid=(.5+.5*math.sin(elapsed*3.1-index*.43))**2
        high=(.5+.5*math.sin(elapsed*7.7+index*.91))**4
        value=.09+(.35+.3*phrase)*(.62*low+.28*mid+.2*high)
        bands.append(min(1,max(0,value)))
    return MusicData(elapsed,'AFTER HOURS','TEKGROAML / DEMO MIX',BPM,elapsed%DURATION,
                     DURATION,beat,.5-.5*math.cos(math.tau*elapsed/8),
                     (.51+elapsed/180)%1,tuple(bands))


def rgb(hue,value=1,saturation=.7):
    return tuple(round(c*255) for c in colorsys.hsv_to_rgb(hue%1,saturation,value))


class MusicDemo:
    path=None

    def read(self,elapsed):return sample(elapsed)
