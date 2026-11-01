"""Animated parcel route, legible pickup reference and three-step timeline."""
from common.neon import WHITE,SOFT,NIGHT,CYAN,PINK,GOLD
from common.signage import AnimatedPanel,canvas,progress,badge
from .model import sample


class ParcelPanel(AnimatedPanel):
    sample=staticmethod(sample)
    def draw(self,p,data,paused=False):
        f=self.frame or data
        accent=(CYAN,GOLD,(137,101,255))[f.stage_index]
        canvas(p,'LOGISTICS / PICKUP SIGNAGE','YOUR PARCEL',accent)
        badge(p,f.order_label,(24,111,136,30),accent)
        p.rect((23,33,57),(24,159,432,150),radius=14)
        p.text(f.status,(240,186),23,WHITE)
        p.line((57,71,98),(72,255),(408,255),4)
        for i in range(3):
            x=72+i*168
            p.circle(accent if i<=f.stage_index else (56,69,95),(x,255),9)
        route=(f.stage_index+f.stage_progress)/3
        x=72+336*route
        p.rect(accent,(x-16,229,32,24),radius=4)
        p.line(WHITE,(x,231),(x,246),2)
        for i,label in enumerate(('PACK','TRANSIT','PICKUP')):
            p.text(label,(72+i*168,285),11,SOFT)
        p.text('COLLECTION REFERENCE',(24,336),14,SOFT,center=False)
        p.text(f.pickup_code,(24,363),43,WHITE,center=False)
        p.text('TEKGROAML',(24,443),16,WHITE,center=False)
        p.text('SAMPLE SHIPMENT',(388,453),12,SOFT)
