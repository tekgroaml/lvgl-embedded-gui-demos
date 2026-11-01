"""Vivid circular drawing helpers; native vectors, no media/audio dependency."""
import colorsys
import math

WHITE=(247,250,255)
SOFT=(167,190,215)
NIGHT=(9,12,28)
PINK=(255,39,163)
CYAN=(0,238,255)
GOLD=(255,210,49)


def color(hue,value=1,saturation=.92):
    return tuple(round(c*255) for c in colorsys.hsv_to_rgb(hue%1,saturation,value))


def mix(a,b,amount):
    return tuple(round(x*amount+y*(1-amount)) for x,y in zip(a,b))


def arc(p,center,radius,start,end,rgb,width=2):
    ctx=p.context;ctx.new_path();p.color(rgb);ctx.set_line_width(width)
    ctx.arc(*center,radius,math.radians(start),math.radians(end));ctx.stroke()


def rainbow_ring(p,radius,width,hue=0,rotation=0,value=1,segments=96,center=(240,240)):
    for i in range(segments):
        angle=rotation+i*360/segments
        arc(p,center,radius,angle,angle+360/segments+.18,color(hue+i/segments,value),width)


def glow(p,center,radius,rgb,power=1):
    for extra,strength in ((24,.025),(16,.05),(9,.1),(3,.22)):
        p.circle(mix(rgb,NIGHT,strength*power),center,radius+extra,8)


def disc(p,hue=.6):
    # Concentric color mixing approximates a soft radial fill with basic Cairo.
    p.circle(NIGHT,(240,240),240)
    for r in range(238,0,-12):
        strength=.07+.13*(1-r/240)
        p.circle(mix(color(hue),NIGHT,strength),(240,240),r)


def icon(p,name,center=(240,190),rgb=CYAN):
    x,y=center
    if name=='music':
        for a,b in (((x-16,y+21),(x-16,y-24)),((x-16,y-24),(x+19,y-32)),
                    ((x+19,y-32),(x+19,y+12))):p.line(rgb,a,b,5)
        p.circle(rgb,(x-24,y+21),10);p.circle(rgb,(x+11,y+12),10)
    elif name=='light':
        for r in (18,31,44):arc(p,center,r,210,510,rgb,4)
        p.line(rgb,(x-10,y+24),(x+10,y+24),4)
        p.line(rgb,(x-7,y+33),(x+7,y+33),4)
    elif name=='clock':
        p.circle(rgb,center,36,4)
        p.line(rgb,center,(x,y-22),4);p.line(rgb,center,(x+19,y+12),4)
        p.circle(WHITE,center,4)
    else:raise ValueError('Unknown same-content demo icon')
