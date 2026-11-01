"""Two circle-safe flight demo panels sharing one linked flight snapshot."""
import math
from gauges.common import BG,TEXT,MUTED,CYAN,AMBER


class AttitudePanel:
    def update(self,dt,data):pass

    def draw(self,p,data,paused=False):
        p.circle((24,37,49),(240,240),228)
        p.circle(BG,(240,240),220)
        p.text('FLIGHT / ATTITUDE',(240,65),20,TEXT)
        p.text(data.phase,(240,89),15,CYAN)
        ctx=p.context
        ctx.save();ctx.new_path();ctx.arc(240,239,142,0,math.tau);ctx.clip()
        ctx.translate(240,239);ctx.rotate(math.radians(-data.bank_deg))
        shift=data.pitch_deg*4
        p.rect((38,96,132),(-400,-400,800,400+shift))
        p.rect((113,76,48),(-400,shift,800,400))
        p.line((231,219,184),(-400,shift),(400,shift),3)
        for pitch in (-20,-10,-5,5,10,20):
            y=shift-pitch*4;width=24 if abs(pitch)==5 else 45
            p.line(TEXT,(-width,y),(width,y),2)
            if abs(pitch)>=10:
                p.text(str(abs(pitch)),(-62,y),13)
                p.text(str(abs(pitch)),(62,y),13)
        ctx.restore()
        p.circle((67,85,99),(240,239),144,3)
        p.line(AMBER,(182,239),(222,239),5)
        p.line(AMBER,(258,239),(298,239),5)
        p.line(AMBER,(222,239),(240,249),4)
        p.line(AMBER,(240,249),(258,239),4)
        for angle in (-60,-30,0,30,60):
            rad=math.radians(angle-90)
            inner=(240+math.cos(rad)*149,239+math.sin(rad)*149)
            outer=(240+math.cos(rad)*159,239+math.sin(rad)*159)
            p.line(MUTED,inner,outer,2)
        p.text(f'HDG {data.heading_deg:03.0f}°',(240,363),24,CYAN)
        p.text(f'BANK {data.bank_deg:+.0f}°   PITCH {data.pitch_deg:+.0f}°',(240,391),15,MUTED)
        p.text('DEMO · SIMULATED FLIGHT',(240,420),13,AMBER)


class AirDataPanel:
    def update(self,dt,data):pass

    def draw(self,p,data,paused=False):
        p.circle((24,37,49),(240,240),228)
        p.circle(BG,(240,240),220)
        for index in range(33):
            speed=40+index*5;degrees=135+(speed-40)/160*270
            major=index%4==0
            p.line(TEXT if major else MUTED,p.polar(198,degrees),p.polar(185 if major else 191,degrees),2 if major else 1)
            if major:p.text(str(speed),p.polar(165,degrees),15,MUTED)
        for low,high,color in [(55,125,(88,178,154)),(125,160,AMBER),(160,190,(224,92,95))]:
            for speed in range(low,high,2):
                degrees=135+(speed-40)/160*270
                p.line(color,p.polar(204,degrees),p.polar(208,degrees),3)
        degrees=135+(data.airspeed_kt-40)/160*270
        p.line(AMBER,p.polar(172,degrees),p.polar(211,degrees),5)
        p.circle(AMBER,p.polar(211,degrees),3)
        p.text('AIR DATA',(240,118),19,TEXT)
        p.text(f'{data.airspeed_kt:03.0f}',(240,190),64,TEXT)
        p.text('KNOTS / IAS',(240,230),16,MUTED)
        p.text(f'{data.altitude_ft:,.0f} FT',(240,283),35,CYAN)
        p.text('ALTITUDE',(240,311),14,MUTED)
        p.text(f'V/S {data.vertical_speed_fpm:+.0f} FPM',(240,346),21,AMBER)
        p.text(data.phase,(240,379),15,MUTED)
        p.text('DEMO · SIMULATED FLIGHT',(240,412),13,AMBER)
