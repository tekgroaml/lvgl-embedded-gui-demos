"""Saturated moving ribbons and a clear ambient-light use-case center card."""
import math
from common.neon import WHITE,SOFT,NIGHT,color,mix,disc,rainbow_ring,glow
from .model import sample


class LightPanel:
    def __init__(self):self.elapsed=None;self.frame=None

    def update(self,dt,data):
        self.elapsed=max(data.elapsed_s,(self.elapsed if self.elapsed is not None else data.elapsed_s)+dt)
        self.frame=sample(self.elapsed)

    def draw(self,p,data,paused=False):
        f=self.frame or data;disc(p,f.hue)
        # Three broad ribbons drift independently around the circular edge.
        for layer,(base,width) in enumerate(((141,15),(169,20),(201,23))):
            points=[]
            for i in range(97):
                angle=i*math.tau/96
                radius=base+7*math.sin(angle*3+f.elapsed_s*.8+layer)
                points.append((240+math.cos(angle)*radius,240+math.sin(angle)*radius))
            for i,(a,b) in enumerate(zip(points,points[1:])):
                p.line(color(f.hue+i/96+layer*.18,.9+.1*math.sin(f.elapsed_s)**2),a,b,width)
        rainbow_ring(p,231,3,f.hue,f.rotation,value=.7)
        p.circle((14,16,39),(240,240),117)
        glow(p,(240,240),111,color(f.hue),.6)
        p.text('TEKGROAML',(240,153),17,WHITE)
        p.text('AMBIENT LIGHT',(240,184),16,WHITE)
        p.text(f'{f.brightness:.0f}%',(240,234),54,WHITE)
        p.text(f.mood,(240,279),15,color(f.hue+.4))
        for i in range(5):p.circle(color(f.hue+i*.15),(204+i*18,309),5)
        p.text('SIMULATED LIGHTING',(240,331),10,SOFT)
