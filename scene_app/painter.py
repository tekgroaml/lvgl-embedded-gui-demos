"""Cairo implementation of the existing view Painter protocol."""
import math
from gauges.common import TEXT


class CairoPainter:
    def __init__(self, context):
        self.context = context

    def color(self, rgb):
        self.context.set_source_rgb(*(component/255 for component in rgb))

    def rect(self, color, bounds, width=0, radius=0):
        ctx = self.context
        x,y,w,h = bounds
        radius = min(radius,w/2,h/2)
        ctx.new_path()
        if radius:
            for cx,cy,start in ((x+w-radius,y+radius,-90),(x+w-radius,y+h-radius,0),
                                (x+radius,y+h-radius,90),(x+radius,y+radius,180)):
                ctx.arc(cx,cy,radius,math.radians(start),math.radians(start+90))
            ctx.close_path()
        else:
            ctx.rectangle(x,y,w,h)
        self.color(color)
        if width:
            ctx.set_line_width(width);ctx.stroke()
        else:
            ctx.fill()

    def line(self, color, a, b, width=1):
        ctx=self.context;ctx.new_path();self.color(color);ctx.set_line_width(width)
        ctx.move_to(*a);ctx.line_to(*b);ctx.stroke()

    def circle(self, color, xy, radius, width=0):
        ctx=self.context;ctx.new_path();self.color(color)
        ctx.arc(*xy,radius,0,math.tau)
        if width:
            ctx.set_line_width(width);ctx.stroke()
        else:
            ctx.fill()

    def text(self, value, xy, size=20, color=TEXT, center=True):
        ctx=self.context;ctx.new_path();self.color(color)
        ctx.select_font_face('DejaVu Sans',0,0)
        # pygame.Font(None,size) uses a smaller em than the nominal point size.
        ctx.set_font_size(size*.76)
        extents=ctx.text_extents(str(value));x,y=xy
        if center:
            x-=extents[0]+extents[2]/2;y-=extents[1]+extents[3]/2
        else:
            y-=extents[1]
        ctx.move_to(x,y);ctx.show_text(str(value));ctx.new_path()

    def polar(self,radius,degrees,center=(240,240)):
        angle=math.radians(degrees)
        return center[0]+radius*math.cos(angle),center[1]+radius*math.sin(angle)


def draw_scene(context, layout, automotive, industrial, data, paused=False):
    context.save()
    context.set_source_rgb(0,0,0);context.paint()
    for panel, view in zip(layout['panels'],(automotive,industrial)):
        rect=panel['rect']
        context.save()
        context.translate(rect['x'],rect['y'])
        context.scale(rect['width']/480,rect['height']/480)
        context.new_path()
        if panel['shape']=='round':
            context.arc(240,240,240,0,math.tau)
        else:
            context.rectangle(0,0,480,480)
        context.clip()
        context.set_source_rgb(9/255,15/255,23/255);context.paint()
        view.draw(CairoPainter(context),data,paused)
        context.restore()
    context.restore()
