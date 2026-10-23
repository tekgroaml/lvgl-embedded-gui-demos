#!/usr/bin/env python3
"""Circular speedometer with a concentric tachometer and redline alerts."""
if __package__ in (None, ''):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import math
from gauges.common import BG, TEXT, MUTED, CYAN, RED, AMBER, run


class AutomotiveGauge:
    def __init__(self):
        self.speed = self.rpm = 0.0

    def update(self, dt, data):
        factor = 1-math.exp(-dt*8)
        self.speed += (data.speed-self.speed)*factor
        self.rpm += (data.rpm-self.rpm)*factor

    def draw(self, p, data, paused=False):
        redline = data.rpm >= 6500
        p.circle((22, 35, 47), (240, 240), 224)
        p.circle(BG, (240, 240), 217)
        for tick in range(61):
            degrees = 135+tick/60*270
            major = tick % 5 == 0
            p.line(TEXT if major else MUTED, p.polar(201, degrees), p.polar(188 if major else 195, degrees), 2 if major else 1)
            if major:
                p.text(tick*5, p.polar(168, degrees), 19)
        for tick in range(81):
            degrees = 135+tick/80*270
            color = RED if tick >= 65 else ((70, 113, 132) if tick > self.rpm/100 else CYAN)
            p.line(color, p.polar(142, degrees), p.polar(133, degrees), 3)
        p.text('VELOCITY / RPM', (240, 142), 18, MUTED)
        p.text(f'{self.speed:03.0f}', (240, 221), 88, TEXT)
        p.text('km/h', (240, 267), 23, MUTED)
        p.text(f'{self.rpm:04.0f} RPM', (240, 311), 28, RED if redline else CYAN)
        p.text('REDLINE' if redline else 'POWERTRAIN', (240, 340), 17, RED if redline else MUTED)
        # Pointer remains near the rim so it does not obscure the digital speed.
        angle = 135+min(300, self.speed)/300*270
        p.line(AMBER, p.polar(177, angle), p.polar(211, angle), 5)
        p.circle(AMBER, p.polar(212, angle), 3)
        p.text(f'{data.temperature:.0f} C    {data.voltage:.1f} V', (240, 375), 20, RED if data.temperature >= 95 else MUTED)
        label = 'DATA STALE' if data.stale else 'SIMULATION PAUSED' if paused else 'SIMULATED DATA' if data.simulated else 'LIVE JSON INPUT'
        p.text(label, (240, 407), 15, RED if data.stale else MUTED)


if __name__ == '__main__': raise SystemExit(run('automotive'))
