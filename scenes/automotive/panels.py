"""Dedicated round-safe road-speed and engine-condition panels."""
import math

from common.theme import BG,TEXT,MUTED,CYAN,AMBER,RED
from common.components import round_frame,demo_footer


class DrivingPanel:
    def __init__(self):
        self.speed=0.;self.rpm=850.

    def update(self,dt,data):
        factor=1-math.exp(-max(0,dt)*10)
        self.speed+=(data.speed_kmh-self.speed)*factor
        self.rpm+=(data.rpm-self.rpm)*factor

    def draw(self,p,data,paused=False):
        round_frame(p,'')
        for i in range(37):
            speed=i*5;degrees=135+speed/180*270
            major=i%4==0
            p.line(TEXT if major else MUTED,p.polar(200,degrees),p.polar(187 if major else 194,degrees),2 if major else 1)
            if major:p.text(str(speed),p.polar(168,degrees),16,MUTED)
        for i in range(61):
            degrees=135+i/60*270
            color=RED if i>=50 else CYAN if i*100<=self.rpm else (41,67,81)
            p.line(color,p.polar(143,degrees),p.polar(136,degrees),3)
        p.text('DRIVE / SPEED',(240,125),19,TEXT)
        p.text(f'{self.speed:03.0f}',(240,209),80,TEXT)
        p.text('km/h',(240,255),23,MUTED)
        p.text(f'{self.rpm:04.0f} RPM',(240,300),27,CYAN)
        gear='N' if data.gear==0 else f'D{data.gear}'
        p.text(gear,(240,337),24,AMBER)
        p.text(data.phase,(240,365),14,MUTED)
        p.text(f'TRIP {data.trip_km:.2f} km',(240,392),17,TEXT)
        degrees=135+max(0,min(180,self.speed))/180*270
        p.line(AMBER,p.polar(176,degrees),p.polar(211,degrees),5)
        p.circle(AMBER,p.polar(211,degrees),3)
        demo_footer(p,'DEMO · SIMULATED DRIVE',423)


class EnginePanel:
    def update(self,dt,data):pass

    def draw(self,p,data,paused=False):
        round_frame(p,'ENGINE / STATUS')
        p.text('COOLANT',(240,112),17,MUTED)
        for i in range(31):
            degrees=150+i/30*240
            value=40+i*3
            color=RED if value>=112 else CYAN if value<=100 else AMBER
            p.line(color if i%5==0 else MUTED,p.polar(200,degrees),p.polar(191,degrees),2)
        p.text(f'{data.coolant_c:.0f}°C',(240,165),47,RED if data.coolant_c>=110 else TEXT)
        p.line((43,66,80),(128,195),(352,195),1)
        p.text('FUEL',(166,222),15,MUTED)
        p.text(f'{data.fuel_percent:.1f}%',(166,258),29,AMBER if data.fuel_percent<15 else CYAN)
        p.text('BATTERY',(311,222),15,MUTED)
        p.text(f'{data.voltage_v:.1f} V',(311,258),28,TEXT)
        p.line((43,66,80),(128,282),(352,282),1)
        p.text('OIL PRESSURE',(240,309),15,MUTED)
        p.text(f'{data.oil_pressure_bar:.2f} bar',(240,341),30,CYAN)
        p.text(f'LOAD {data.load_percent:.0f}%   FUEL {data.fuel_rate_lph:.1f} L/h',(240,377),16,MUTED)
        p.text(data.phase,(240,401),13,MUTED)
        demo_footer(p,'DEMO · SIMULATED ENGINE',426)
