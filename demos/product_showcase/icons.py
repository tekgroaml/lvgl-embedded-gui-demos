"""Local vector application icons; no downloaded assets or icon-font dependency."""
import math
from common.theme import CYAN,AMBER


def polygon(ctx,points,rgb):
    ctx.new_path();ctx.set_source_rgb(*(v/255 for v in rgb))
    ctx.move_to(*points[0])
    for point in points[1:]:ctx.line_to(*point)
    ctx.close_path();ctx.fill()


def aircraft(p):
    polygon(p.context,[(240,123),(251,144),(251,181),(307,214),(307,228),(250,212),
                       (250,248),(266,264),(266,274),(240,264),(214,274),(214,264),
                       (230,248),(230,212),(173,228),(173,214),(229,181),(229,144)],CYAN)


def car(p):
    p.line(CYAN,(161,215),(173,186),5)
    p.line(CYAN,(173,186),(202,186),5)
    p.line(CYAN,(202,186),(217,216),5)
    p.rect(CYAN,(145,214,88,35),3,7)
    p.line(CYAN,(162,216),(217,216),3)
    p.circle(AMBER,(165,251),10,3);p.circle(AMBER,(214,251),10,3)
    p.line(CYAN,(146,229),(158,229),3);p.line(CYAN,(222,229),(232,229),3)


def motorcycle(p):
    p.circle(AMBER,(267,248),17,3);p.circle(AMBER,(329,248),17,3)
    for a,b in [((267,248),(289,216)),((289,216),(312,248)),((312,248),(267,248)),
                ((312,248),(318,203)),((318,203),(329,248)),((310,202),(327,202)),
                ((282,211),(300,211))]:p.line(CYAN,a,b,4)
    p.line(CYAN,(289,216),(312,216),4)
    polygon(p.context,[(284,214),(299,208),(313,216),(303,228),(284,224)],CYAN)
    p.rect(AMBER,(284,229,20,13),radius=3)
    p.rect(CYAN,(278,203,24,5),radius=2)
    p.line(AMBER,(283,249),(312,254),3)


def computer(p):
    p.rect(CYAN,(188,126,105,153),4,10)
    p.rect(CYAN,(200,139,81,111),2,5)
    for cy in (168,215):
        p.circle(AMBER,(240,cy),17,2)
        for angle in (0,120,240):
            radians=math.radians(angle)
            p.line(AMBER,(240,cy),(240+math.cos(radians)*12,cy+math.sin(radians)*12),3)
    p.circle(CYAN,(268,265),3)
    p.line(CYAN,(207,282),(207,291),4);p.line(CYAN,(274,282),(274,291),4)


def home(p):
    for a,b in (((161,196),(240,133)),((240,133),(319,196)),
                ((176,186),(176,277)),((176,277),(304,277)),((304,277),(304,186))):
        p.line(CYAN,a,b,5)
    p.rect(AMBER,(219,227,42,50),width=3,radius=3)
    p.rect(CYAN,(193,193,25,23),width=3,radius=3)
    p.rect(CYAN,(263,193,25,23),width=3,radius=3)
    p.circle(AMBER,(316,135),15,width=3)


def factory(p):
    points=[(164,276),(164,205),(204,183),(204,205),(245,181),(245,205),
            (277,186),(277,143),(300,143),(308,276),(164,276)]
    for a,b in zip(points,points[1:]):p.line(CYAN,a,b,4)
    for x in (184,221,258):p.rect(AMBER,(x,231,18,20),width=2,radius=2)
    p.line(AMBER,(284,128),(295,116),3)
    p.line(AMBER,(299,124),(310,112),3)


def draw_icon(p,name):
    if name=='aircraft':aircraft(p)
    elif name=='vehicle':car(p);motorcycle(p)
    elif name=='computer':computer(p)
    elif name=='home':home(p)
    elif name=='factory':factory(p)
    else:raise ValueError('Unknown product icon')
