#!/usr/bin/env python3
"""Square industrial sensor panel with sampled waveform, LEDs and alarms."""
if __package__ in (None, ''):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collections import deque
from gauges.common import BG, PANEL, TEXT, MUTED, CYAN, RED, AMBER, run


class IndustrialPanel:
    def __init__(self):
        self.history = deque([0.0]*180, maxlen=180)
        self.accumulator = 0.0

    def update(self, dt, data):
        self.accumulator += dt
        # A fixed 30 Hz display sample rate is independent of rendering FPS.
        while self.accumulator + 1e-12 >= 1/30:
            self.history.append(None if data.stale else data.signal)
            self.accumulator -= 1/30

    def draw(self, p, data, paused=False):
        alarm = data.temperature >= 95 or data.pressure >= 8
        p.text('FIELD / 01', (26, 25), 24, TEXT, center=False)
        p.text('PROCESS TELEMETRY', (26, 54), 15, MUTED, center=False)
        for index, (label, active, color) in enumerate((('LINK', not data.stale, CYAN), ('WARN', alarm, AMBER), ('FAULT', data.stale, RED))):
            x = 300+index*61
            p.circle(color if active else (42, 55, 68), (x, 30), 5)
            p.text(label, (x, 49), 12, MUTED)
        p.rect(PANEL, (22, 87, 436, 196), radius=12)
        p.text('SIGNAL / NORMALIZED', (38, 100), 15, MUTED, center=False)
        for x in range(38, 445, 29): p.line((32, 52, 65), (x, 128), (x, 263))
        for y in range(128, 264, 27): p.line((32, 52, 65), (38, y), (444, y))
        p.line((61, 92, 106), (38, 196), (444, 196))
        points = [(38+i/(len(self.history)-1)*406, 196-value*58) if value is not None else None for i, value in enumerate(self.history)]
        for left, right in zip(points, points[1:]):
            if left is not None and right is not None: p.line(CYAN, left, right, 2)
        cells = [('TEMPERATURE', f'{data.temperature:05.1f}', 'C', data.temperature >= 95),
                 ('PRESSURE', f'{data.pressure:04.1f}', 'bar', data.pressure >= 8),
                 ('BUS VOLTAGE', f'{data.voltage:04.1f}', 'V', data.voltage < 11),
                 ('SHAFT SPEED', f'{data.rpm:04.0f}', 'RPM', data.rpm >= 6500)]
        for i, (label, value, unit, warning) in enumerate(cells):
            x, y = 22+(i % 2)*223, 301+(i//2)*73
            p.rect(PANEL, (x, y, 213, 64), radius=8)
            p.text(label, (x+12, y+9), 13, MUTED, center=False)
            p.text(value, (x+12, y+26), 33, RED if warning else TEXT, center=False)
            p.text(unit, (x+152, y+37), 17, MUTED, center=False)
        label = 'DATA STALE' if data.stale else 'SIMULATION PAUSED' if paused else 'SIMULATED DATA' if data.simulated else 'LIVE JSON INPUT'
        p.text(label, (27, 460), 14, RED if data.stale else MUTED, center=False)
        p.text('30 Hz / 6 s', (399, 460), 14, MUTED)


if __name__ == '__main__': raise SystemExit(run('industrial'))
