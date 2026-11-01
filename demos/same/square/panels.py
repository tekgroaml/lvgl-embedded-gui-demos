"""Full-square brand and use-case intro, duplicated identically on both panels."""
import math
from common.neon import WHITE,SOFT,NIGHT,CYAN,PINK,GOLD
from common.signage import progress
from demos.shared.panels import ShowcasePanel,fitted_text


class SquareSamePanel(ShowcasePanel):
    warmup_seconds=0.
    def __init__(self):super().__init__(0)

    def draw(self,p,data,paused=False):
        if data.phase=='effect':
            super().draw(p,data,paused)
            return
        accent=(PINK,(67,255,142),GOLD)[data.stage_index]
        p.rect(NIGHT,(0,0,480,480))
        p.rect(accent,(0,0,480,12))
        p.text('TEKGROAML',(24,39),28,WHITE,center=False)
        p.text('SQUARE DISPLAYS / SAME CONTENT',(24,82),13,SOFT,center=False)
        p.rect((24,34,59),(24,125,432,132),radius=16)
        if data.icon=='store':
            p.rect(accent,(202,168,76,58),width=4,radius=5)
            p.line(accent,(196,168),(211,148),4);p.line(accent,(211,148),(269,148),4);p.line(accent,(269,148),(284,168),4)
            p.line(accent,(196,168),(284,168),4)
        elif data.icon=='room':
            p.rect(accent,(211,147,58,84),width=4,radius=4)
            p.circle(accent,(254,191),4)
        else:
            p.rect(accent,(199,155,82,68),width=4,radius=5)
            p.line(accent,(240,155),(240,190),4);p.line(accent,(226,190),(254,190),4)
        fitted_text(p,data.title,(240,304),31,422,WHITE)
        fitted_text(p,data.subtitle,(240,347),17,420,SOFT)
        remain=max(1,math.ceil(data.phase_duration-data.phase_elapsed))
        p.text(f'STARTING IN {remain}s',(24,394),15,accent,center=False)
        p.text(f'{data.stage_index+1:02d} / 03',(426,405),16,WHITE)
        progress(p,data.phase_elapsed/data.phase_duration,(24,435,432,6),accent)
        p.text('PRODUCT USE CASE DEMO',(240,461),11,SOFT)
