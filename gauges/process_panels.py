"""Square pump-station overview and correlated process-trend dashboard."""
from collections import deque
from gauges.common import BG,PANEL,TEXT,MUTED,CYAN,AMBER,RED


def card(p,label,value,unit,x,y,width=207):
    p.rect(PANEL,(x,y,width,66),radius=8)
    p.text(label,(x+12,y+10),13,MUTED,center=False)
    p.text(value,(x+12,y+29),31,TEXT,center=False)
    p.text(unit,(x+width-44,y+43),14,MUTED)


class PumpPanel:
    def __init__(self):self.elapsed=0.;self.angle=0.
    def update(self,dt,data):
        self.elapsed+=dt
        self.angle=(self.angle+dt*(data.rpm/3000)*4)%6.283185307179586

    def draw(self,p,data,paused=False):
        p.text('PUMP STATION / 01',(26,20),25,TEXT,center=False)
        p.text(data.phase,(26,51),15,CYAN,center=False)
        p.circle(CYAN if data.rpm>100 else AMBER,(444,31),6)
        p.rect(PANEL,(22,84,436,181),radius=12)
        p.rect((29,47,63),(48,129,80,72),radius=9)
        p.text('MOTOR',(88,151),14,MUTED)
        p.text(f'{data.rpm:04.0f}',(88,178),25,CYAN)
        p.line(MUTED,(129,166),(165,166),6)
        p.circle((31,55,67),(193,166),33)
        p.circle(CYAN,(193,166),27,2)
        import math
        angle=self.angle
        for i in range(3):
            rad=angle+i*math.tau/3
            p.line(CYAN,(193,166),(193+math.cos(rad)*21,166+math.sin(rad)*21),4)
        p.line((45,77,93),(226,166),(291,166),10)
        p.line((45,77,93),(291,166),(291,126),10)
        p.line((45,77,93),(291,126),(353,126),10)
        p.rect((34,58,73),(353,109,72,114),radius=7)
        level=min(1,max(0,(data.pressure_bar-1.1)/5.5))
        p.rect((39,124,139),(360,210-level*88,58,6+level*88),radius=3)
        p.text('BUFFER',(389,240),12,MUTED)
        if data.flow_lmin>1:
            for i in range(3):
                x=236+((self.elapsed*22+i*17)%49)
                p.line(CYAN,(x-3,163),(x+3,166),2)
                p.line(CYAN,(x+3,166),(x-3,169),2)
        p.text('CIRCULATION LOOP',(240,96),12,MUTED)
        card(p,'DRIVE SPEED',f'{data.rpm:04.0f}','RPM',22,282)
        card(p,'MOTOR LOAD',f'{data.load_percent:04.1f}','%',251,282)
        card(p,'OUTLET PRESSURE',f'{data.pressure_bar:.2f}','bar',22,362)
        card(p,'DELIVERY FLOW',f'{data.flow_lmin:.1f}','L/min',251,362)
        p.text('DEMO · AUTOMATIC DUTY CYCLE',(25,455),13,AMBER,center=False)


class ProcessTrends:
    def __init__(self):
        self.samples=deque(maxlen=300);self.accumulator=0.
    def update(self,dt,data):
        self.accumulator+=dt
        while self.accumulator+1e-12>=.2:
            self.samples.append((data.pressure_bar,data.temperature_c))
            self.accumulator-=.2

    def draw(self,p,data,paused=False):
        p.text('PROCESS / CONDITION',(26,20),24,TEXT,center=False)
        p.text('PRESSURE + THERMAL RESPONSE',(26,51),13,MUTED,center=False)
        p.rect(PANEL,(22,86,436,184),radius=12)
        p.text('0–8 bar',(42,102),12,CYAN,center=False)
        p.text('20–70°C',(348,102),12,AMBER,center=False)
        for y in range(130,251,30):p.line((34,55,68),(40,y),(440,y))
        for x in range(40,441,50):p.line((34,55,68),(x,130),(x,250))
        values=list(self.samples)
        offset=300-len(values)
        for i in range(1,len(values)):
            x1=40+(offset+i-1)*400/299;x2=40+(offset+i)*400/299
            a,b=values[i-1],values[i]
            p.line(CYAN,(x1,250-max(0,min(1,a[0]/8))*120),(x2,250-max(0,min(1,b[0]/8))*120),2)
            p.line(AMBER,(x1,250-max(0,min(1,(a[1]-20)/50))*120),(x2,250-max(0,min(1,(b[1]-20)/50))*120),2)
        card(p,'BEARING TEMPERATURE',f'{data.temperature_c:.1f}','°C',22,286)
        card(p,'VIBRATION',f'{data.vibration_mm_s:.2f}','mm/s',251,286)
        card(p,'DRIVE POWER',f'{data.power_kw:.1f}','kW',22,366)
        card(p,'DELIVERED TOTAL',f'{data.produced_liters:.1f}','L',251,366)
        p.text('DEMO · SIMULATED PROCESS',(25,455),13,AMBER,center=False)
        p.text('60 s',(429,458),12,MUTED)
