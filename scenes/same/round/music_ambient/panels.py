"""Vivid circular spectrum, breathing neon halo and simulated playback card."""
from common.neon import WHITE,SOFT,NIGHT,color,mix,disc,rainbow_ring,glow
from .model import sample


def timecode(seconds):
    seconds=int(seconds)
    return f'{seconds//60:02d}:{seconds%60:02d}'


class MusicPanel:
    def __init__(self):self.elapsed=None;self.frame=None

    def update(self,dt,data):
        self.elapsed=max(data.elapsed_s,(self.elapsed if self.elapsed is not None else data.elapsed_s)+dt)
        self.frame=sample(self.elapsed)

    def draw(self,p,data,paused=False):
        f=self.frame or data;ctx=p.context
        hue=f.hue+.28
        accent=color(hue+.2)
        disc(p,hue)
        rainbow_ring(p,229,4,hue,f.elapsed_s*4,value=.8)
        glow(p,(240,240),207+f.breath*6,accent,.8)
        for i,level in enumerate(f.bands):
            angle=-90+i*360/len(f.bands)
            rgb=color(hue+i/len(f.bands)*.8)
            a=p.polar(178,angle);b=p.polar(190+level*64,angle)
            p.line(mix(rgb,NIGHT,.18),a,p.polar(224,angle),5)
            p.line(rgb,a,b,5)
            p.circle(WHITE,b,1.2)
        p.text('MUSIC / AMBIENT',(240,94),12,SOFT)
        p.text('TEKGROAML',(240,125),21,WHITE)
        p.circle((22,17,45),(240,210),54)
        for r in (49,44,39):p.circle(mix(accent,NIGHT,.3),(240,210),r,1)
        p.circle(accent,(240,210),30+f.beat*7,3)
        ctx.new_path();p.color(WHITE)
        ctx.move_to(232,197);ctx.line_to(253,210);ctx.line_to(232,223)
        ctx.close_path();ctx.fill()
        p.text(f.title,(240,286),29,WHITE)
        p.text(f.artist,(240,315),12,SOFT)
        p.line((46,45,77),(167,340),(313,340),4)
        end=167+146*f.track_seconds/f.duration_seconds
        p.line(accent,(167,340),(end,340),4)
        p.circle(WHITE,(end,340),3)
        p.text(timecode(f.track_seconds),(175,360),12,SOFT)
        p.text(f'{f.bpm} BPM',(240,360),12,accent)
        p.text(timecode(f.duration_seconds),(306,360),12,SOFT)
        p.circle(color(hue+.55),(173,387),2)
        p.text('SIMULATED AUDIO',(246,387),12,SOFT)
        if data.stale:p.text('DATA STALE',(240,409),12,(255,96,99))
