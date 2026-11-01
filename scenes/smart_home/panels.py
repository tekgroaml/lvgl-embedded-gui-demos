"""Square-specific climate cards and an animated home-energy flow diagram."""
from common.components import card
from common.square import header,footer,load_bar,fan,History
from common.theme import PANEL,TEXT,MUTED,CYAN,AMBER


class ClimatePanel:
    def __init__(self):self.history=History();self.angle=0.

    def update(self,dt,data):
        self.history.update(dt,(data.temperature_c,data.target_c))
        self.angle+=dt*3

    def draw(self,p,data,paused=False):
        header(p,'SMART HOME / CLIMATE','LIVING ROOM · COMFORT AUTOMATION')
        p.rect(PANEL,(22,94,436,134),radius=12)
        p.text('ROOM TEMPERATURE',(42,110),15,MUTED,center=False)
        p.text(f'{data.temperature_c:.1f}°C',(42,139),64,TEXT,center=False)
        p.text(f'TARGET {data.target_c:.1f}°C · {data.hvac}',(42,202),15,CYAN,center=False)
        fan(p,(397,160),38,self.angle)
        card(p,'HUMIDITY',f'{data.humidity_pct:.0f}','%',22,242)
        card(p,'HVAC POWER',f'{data.hvac_w:.0f}','W',251,242)
        load_bar(p,'LIGHTING',data.light_pct,42,326,width=388)
        p.text('ROOM / TARGET · LAST 10s',(42,379),12,MUTED,center=False)
        self.history.draw(p,(42,402,388,34),((21,24),(21,24)))
        footer(p)


class EnergyPanel:
    def __init__(self):self.clock=0.

    def update(self,dt,data):self.clock=data.elapsed_s

    def draw(self,p,data,paused=False):
        header(p,'SMART HOME / ENERGY','SOLAR + HOME + GRID · BALANCED FLOW')
        p.rect(PANEL,(22,94,436,213),radius=12)
        for x,label,value,color in ((95,'SOLAR',data.solar_w,CYAN),(385,'GRID',abs(data.grid_w),AMBER)):
            p.rect((27,47,60),(x-56,126,112,78),radius=8)
            p.text(label,(x,142),14,color)
            p.text(f'{value:.0f} W',(x,177),25,TEXT)
        p.rect((29,65,72),(182,213,116,72),radius=8)
        p.text('HOME',(240,230),14,CYAN)
        p.text(f'{data.house_w:.0f} W',(240,262),24,TEXT)
        for start,end in (((151,164),(240,213)),(((240,213),(329,164)) if data.grid_w<0 else ((329,164),(240,213)))):
            p.line((57,88,99),start,end,3)
            for i in range(3):
                u=(self.clock*.5+i/3)%1
                p.circle(CYAN,(start[0]+(end[0]-start[0])*u,start[1]+(end[1]-start[1])*u),4)
        card(p,'SOLAR GENERATION',f'{data.solar_w/1000:.2f}','kW',22,324)
        card(p,'HOME CONSUMPTION',f'{data.house_w/1000:.2f}','kW',251,324)
        direction='IMPORTING FROM GRID' if data.grid_w>=0 else 'EXPORTING TO GRID'
        p.text(f'{direction}  {abs(data.grid_w):.0f} W',(240,421),18,AMBER)
        footer(p)
