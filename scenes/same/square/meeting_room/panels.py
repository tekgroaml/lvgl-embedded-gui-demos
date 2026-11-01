"""Room name, large status card, animated schedule strip and sample capacity."""
from common.neon import WHITE,SOFT,NIGHT,CYAN,PINK,GOLD
from common.signage import AnimatedPanel,canvas,progress,badge
from .model import sample


class RoomPanel(AnimatedPanel):
    sample=staticmethod(sample)
    def draw(self,p,data,paused=False):
        f=self.frame or data
        accent=((67,255,142),GOLD,PINK)[f.status_index]
        canvas(p,'WORKSPACE / ROOM SIGNAGE','STUDIO 01',accent)
        p.text('6 SEATS  /  DEMO SCHEDULE',(24,102),15,SOFT,center=False)
        p.rect(accent,(24,145,432,124),radius=15)
        p.text(f.status,(240,185),37,NIGHT)
        p.text(f.label,(240,232),17,NIGHT)
        p.text('NEXT STATUS IN',(24,295),14,SOFT,center=False)
        p.text(f'{max(1,int(f.seconds_remaining+.999)):02d}s',(394,310),30,WHITE)
        progress(p,f.phase_progress,(24,336,432,8),accent)
        for i,label in enumerate(('FREE','SOON','BUSY')):
            x=24+i*148
            p.rect(accent if i==f.status_index else (27,36,56),(x,369,136,46),radius=8)
            p.text(label,(x+68,392),15,NIGHT if i==f.status_index else SOFT)
        p.text('TEKGROAML',(24,443),16,WHITE,center=False)
        p.text('DEMO CALENDAR',(390,453),12,SOFT)
