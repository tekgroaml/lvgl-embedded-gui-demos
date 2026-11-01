"""Bright analog hands, digital seconds and clearly simulated desktop info."""
import math
from common.neon import WHITE,SOFT,NIGHT,PINK,CYAN,GOLD,color,mix,disc,rainbow_ring,glow
from .model import sample


class ClockPanel:
    def __init__(self):self.elapsed=None;self.frame=None

    def update(self,dt,data):
        self.elapsed=max(data.elapsed_s,(self.elapsed if self.elapsed is not None else data.elapsed_s)+dt)
        self.frame=sample(self.elapsed)

    def draw(self,p,data,paused=False):
        f=self.frame or data;hue=.56+f.elapsed_s/100
        disc(p,hue)
        rainbow_ring(p,220,11,hue,-90)
        rainbow_ring(p,232,2,hue+.22,f.elapsed_s*4,value=.6)
        p.text('TEKGROAML',(240,66),18,WHITE)
        p.text(f.date_label,(240,101),15,CYAN)
        center=(240,230)
        p.circle((12,18,39),center,102)
        glow(p,center,99,PINK,.7)
        for i in range(60):
            angle=i*6-90;length=11 if i%5==0 else 4
            p.line(color(hue+i/60),p.polar(94-length,angle,center),p.polar(94,angle,center),3 if i%5==0 else 1)
        for number,angle in (('12',-90),('3',0),('6',90),('9',180)):
            p.text(number,p.polar(68,angle,center),15,WHITE)
        hour_angle=(f.hour%12+f.minute/60+f.second/3600)*30-90
        minute_angle=(f.minute+f.second/60)*6-90
        second_angle=f.second*6-90
        p.line(WHITE,center,p.polar(43,hour_angle,center),6)
        p.line(CYAN,center,p.polar(65,minute_angle,center),4)
        p.line(PINK,p.polar(-14,second_angle,center),p.polar(81,second_angle,center),2)
        p.circle(GOLD,center,5)
        p.text(f'{f.hour:02d}:{f.minute:02d}:{int(f.second):02d}',(240,355),40,WHITE)
        p.circle(GOLD,(173,390),8)
        for i in range(8):
            angle=i*45
            p.line(GOLD,p.polar(11,angle,(173,390)),p.polar(15,angle,(173,390)),2)
        p.text(f'{f.weather} {f.temperature_c}°C',(258,390),18,WHITE)
        p.text('DEMO TIME / SAMPLE WEATHER',(240,419),10,SOFT)
