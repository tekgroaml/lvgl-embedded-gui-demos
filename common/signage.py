"""Shared square signage composition and deterministic visual interpolation."""
from common.neon import WHITE,SOFT,NIGHT,CYAN,PINK,color


class AnimatedPanel:
    sample=None
    def __init__(self):self.elapsed=None;self.frame=None
    def update(self,dt,data):
        self.elapsed=max(data.elapsed_s,(self.elapsed if self.elapsed is not None else data.elapsed_s)+dt)
        self.frame=self.sample(self.elapsed)


def canvas(p,eyebrow,title,accent=CYAN):
    p.rect(NIGHT,(0,0,480,480))
    p.rect(accent,(0,0,480,8))
    p.text(eyebrow,(24,28),14,accent,center=False)
    p.text(title,(24,59),30,WHITE,center=False)


def progress(p,value,bounds,accent=CYAN):
    x,y,w,h=bounds
    p.rect((35,44,65),bounds,radius=h/2)
    p.rect(accent,(x,y,max(1,w*max(0,min(1,value))),h),radius=h/2)


def badge(p,text,bounds,accent=CYAN):
    x,y,w,h=bounds
    p.rect(accent,bounds,radius=8)
    p.text(text,(x+w/2,y+h/2),15,NIGHT)
