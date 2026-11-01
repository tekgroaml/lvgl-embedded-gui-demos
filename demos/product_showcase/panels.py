"""Title cards plus direct reuse of the existing three scene panel factories."""
import math
from common.components import round_frame
from common.theme import TEXT,MUTED,CYAN,AMBER
from .icons import draw_icon


def fitted_text(p,text,xy,size,max_width,color=TEXT):
    ctx=p.context
    ctx.select_font_face('DejaVu Sans',0,0);ctx.set_font_size(size*.76)
    width=ctx.text_extents(text)[2]
    p.text(text,xy,size if width<=max_width else size*max_width/width,color)


class ShowcasePanel:
    def __init__(self,index):
        self.index=index
        self.token=None
        self.panel=None

    def select_panel(self,data):
        if data.phase!='effect':return
        token=(data.cycle_index,data.stage_index)
        if token!=self.token:
            from scenes.registry import definition
            self.panel=definition(data.scene).create_panels()[self.index]
            # Start effects in an active phase rather than displaying ten seconds
            # of car idle / PC idle; only the data model is prewarmed.
            self.panel.update(1.,data.payload)
            self.token=token

    def update(self,dt,data):
        self.select_panel(data)
        if data.phase=='effect':self.panel.update(dt,data.payload)

    def draw(self,p,data,paused=False):
        if data.phase=='effect':
            self.select_panel(data)
            self.panel.draw(p,data.payload,paused)
            return
        if self.index==0:
            self.draw_brand(p,data)
        else:
            self.draw_application(p,data)

    def draw_brand(self,p,data):
        round_frame(p,'')
        fitted_text(p,'TEKGROAML',(240,90),34,328,TEXT)
        draw_icon(p,data.icon)
        fitted_text(p,'YOUR IDEAS. ON DISPLAY.',(240,344),18,292,CYAN)
        p.text('DUAL ROUND DISPLAYS',(240,378),15,MUTED)
        p.text(f'{data.stage_index+1:02d} / 03',(240,408),14,AMBER)
        p.text('PRODUCT DEMO · SIMULATED DATA',(240,431),11,MUTED)

    def draw_application(self,p,data):
        round_frame(p,'')
        p.text('APPLICATION SCENARIO',(240,94),16,CYAN)
        fitted_text(p,data.title,(240,164),28,326,TEXT)
        fitted_text(p,data.subtitle,(240,206),17,320,MUTED)
        p.line((46,68,82),(132,239),(348,239),1)
        p.text('SCREEN 1',(240,269),13,AMBER)
        fitted_text(p,data.panel_labels[0],(240,299),20,326,TEXT)
        p.text('SCREEN 2',(240,339),13,AMBER)
        fitted_text(p,data.panel_labels[1],(240,369),20,302,TEXT)
        remaining=max(1,math.ceil(data.phase_duration-data.phase_elapsed))
        p.text(f'STARTING IN {remaining}s',(240,409),14,CYAN)
        p.text('PRODUCT DEMO · SIMULATED DATA',(240,431),11,MUTED)


class LeftPanel(ShowcasePanel):
    def __init__(self):super().__init__(0)


class RightPanel(ShowcasePanel):
    def __init__(self):super().__init__(1)
