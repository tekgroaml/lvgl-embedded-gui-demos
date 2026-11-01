"""Small reusable drawing components on the 480-unit panel canvas."""
from common.theme import BG,PANEL,TEXT,MUTED,CYAN,AMBER,RED

def card(p,label,value,unit,x,y,width=207):
    p.rect(PANEL,(x,y,width,66),radius=8)
    p.text(label,(x+12,y+10),13,MUTED,center=False)
    p.text(value,(x+12,y+29),31,TEXT,center=False)
    p.text(unit,(x+width-44,y+43),14,MUTED)


def round_frame(p, title, subtitle=None):
    p.circle((24,37,49),(240,240),228)
    p.circle(BG,(240,240),220)
    p.text(title,(240,65),20,TEXT)
    if subtitle:p.text(subtitle,(240,89),15,CYAN)


def demo_footer(p, value, y=420):
    p.text(value,(240,y),13,AMBER)
