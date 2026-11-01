"""Same introduction on both circles; reuse scene factories for each effect."""
import math
from demos.shared.panels import ShowcasePanel,fitted_text
from common.neon import WHITE,SOFT,CYAN,PINK,color,disc,rainbow_ring,icon


class SamePanel(ShowcasePanel):
    warmup_seconds=0.
    def __init__(self):super().__init__(0)

    def draw(self,p,data,paused=False):
        if data.phase=='effect':
            super().draw(p,data,paused)
            return
        hue=(.82,.46,.61)[data.stage_index]
        disc(p,hue)
        rainbow_ring(p,219,12,hue,data.phase_elapsed*13)
        rainbow_ring(p,231,2,hue+.2,value=.7)
        p.text('TEKGROAML',(240,89),29,WHITE)
        p.text(f'{data.stage_index+1:02d} / 03',(240,122),13,SOFT)
        p.circle(color(hue,.25),(240,194),55)
        icon(p,data.icon,(240,194),color(hue+.28))
        fitted_text(p,data.title,(240,282),29,316,WHITE)
        fitted_text(p,data.subtitle,(240,316),15,310,SOFT)
        p.text(f'STARTING IN {max(1,math.ceil(data.phase_duration-data.phase_elapsed))}s',(240,365),15,CYAN)
        p.text('DUAL ROUND / SAME CONTENT',(240,399),12,WHITE)
        p.text('PRODUCT DEMO',(240,422),10,SOFT)
