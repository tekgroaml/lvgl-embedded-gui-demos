"""Full-square offer card with animated drink illustration and changing sample offers."""
import math
from common.neon import WHITE,SOFT,NIGHT,CYAN,PINK,GOLD,color
from common.signage import AnimatedPanel,canvas,progress,badge
from .model import sample


class StorePanel(AnimatedPanel):
    sample=staticmethod(sample)
    def draw(self,p,data,paused=False):
        f=self.frame or data
        accent=(PINK,CYAN,(125,255,73))[f.offer_index]
        canvas(p,'RETAIL / COUNTER SIGNAGE','FRESH FINDS',accent)
        badge(p,f.category,(24,111,180,30),accent)
        p.rect((24,31,56),(24,157,432,143),radius=14)
        # Large illustrative cup: no remote product imagery or fonts.
        p.rect(accent,(318,192,86,75),radius=9)
        p.line(WHITE,(310,188),(412,188),6)
        p.line(WHITE,(382,188),(394,164),5)
        for j in range(3):
            y=208+((f.elapsed_s*13+j*17)%45)
            p.circle((255,255,255),(336+j*21,y),3)
        p.text('SAMPLE OFFER',(44,182),13,SOFT,center=False)
        p.text(f.price,(44,220),51,WHITE,center=False)
        p.text(f.product,(24,319),28,WHITE,center=False)
        p.text(f.tagline,(24,357),17,SOFT,center=False)
        progress(p,1-f.offer_progress,(24,400,432,8),accent)
        p.text('TEKGROAML',(24,443),16,WHITE,center=False)
        p.text('DEMO PRICES',(394,453),12,SOFT)
