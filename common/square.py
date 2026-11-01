"""Shared square-dashboard headers, load bars, fans and bounded histories."""
from collections import deque
import math
from common.theme import PANEL,TEXT,MUTED,CYAN,AMBER


def header(p,title,subtitle):
    p.text(title,(24,22),25,TEXT,center=False)
    p.text(subtitle,(24,54),14,CYAN,center=False)
    p.line((38,60,75),(24,78),(456,78))


def footer(p,label='SIMULATED DATA · AUTO DEMO'):
    p.text(label,(24,455),12,AMBER,center=False)


def load_bar(p,label,value,x,y,width=392,color=CYAN):
    p.text(label,(x,y),15,MUTED,center=False)
    p.text(f'{value:.0f}%',(x+width,y+5),20,color)
    p.rect((32,49,63),(x,y+26,width,10),radius=5)
    p.rect(color,(x,y+26,max(1,width*max(0,min(100,value))/100),10),radius=5)


def fan(p,center,radius,angle,color=CYAN):
    x,y=center
    p.circle((39,60,74),center,radius,2)
    for i in range(5):
        a=angle+i*math.tau/5
        b=a+.48
        p.line(color,(x+math.cos(a)*radius*.23,y+math.sin(a)*radius*.23),
               (x+math.cos(b)*radius*.8,y+math.sin(b)*radius*.8),6)
    p.circle(AMBER,center,5)


class History:
    """Keep at most 10s of real demo samples; never invent pre-start history."""
    def __init__(self):
        self.samples=deque(maxlen=51)
        self.clock=0.
        self.next_sample=0.

    def update(self,dt,values):
        self.clock+=dt
        if self.clock>=self.next_sample:
            self.samples.append((self.clock,tuple(values)))
            self.next_sample=self.clock+.2

    def draw(self,p,bounds,ranges,colors=(CYAN,AMBER)):
        x,y,w,h=bounds
        for i in range(5):p.line((34,52,67),(x,y+h*i/4),(x+w,y+h*i/4))
        samples=list(self.samples)
        for k,((low,high),color) in enumerate(zip(ranges,colors)):
            for a,b in zip(samples,samples[1:]):
                if a[0]<self.clock-10:continue
                pa=(x+w*(1-(self.clock-a[0])/10),y+h*(1-max(0,min(1,(a[1][k]-low)/(high-low)))))
                pb=(x+w*(1-(self.clock-b[0])/10),y+h*(1-max(0,min(1,(b[1][k]-low)/(high-low)))))
                p.line(color,pa,pb,2)
