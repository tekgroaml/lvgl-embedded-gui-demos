"""CPU/memory and GPU/cooling cards designed for the full square canvas."""
from common.components import card
from common.square import header,footer,load_bar,fan,History
from common.theme import PANEL,TEXT,MUTED,CYAN,AMBER


class SystemPanel:
    def __init__(self):self.history=History()

    def update(self,dt,data):self.history.update(dt,(data.cpu_load_pct,data.gpu_load_pct))

    def draw(self,p,data,paused=False):
        header(p,'PC CASE / SYSTEM',data.workload+' · SIMULATED PC')
        p.rect(PANEL,(22,94,436,136),radius=12)
        p.text('CPU LOAD',(42,110),15,MUTED,center=False)
        p.text(f'{data.cpu_load_pct:.0f}%',(42,142),63,CYAN,center=False)
        p.text(f'{data.cpu_temp_c:.1f}°C',(350,160),34,TEXT)
        p.text(f'{data.cpu_power_w:.0f} W',(350,202),20,AMBER)
        load_bar(p,'MEMORY',data.memory_used_gb/data.memory_total_gb*100,42,247,width=388)
        p.text(f'{data.memory_used_gb:.1f} / {data.memory_total_gb:.0f} GB',(240,307),17,TEXT)
        p.rect(PANEL,(22,330,436,110),radius=10)
        p.text('CPU / GPU LOAD · LAST 10s',(42,344),13,MUTED,center=False)
        self.history.draw(p,(42,376,388,46),((0,100),(0,100)))
        footer(p)


class CoolingPanel:
    def __init__(self):self.angle=0.

    def update(self,dt,data):self.angle+=dt*data.gpu_fan_rpm/180

    def draw(self,p,data,paused=False):
        header(p,'PC CASE / GPU + COOLING','THERMAL RESPONSE · FANS FOLLOW LOAD')
        p.rect(PANEL,(22,94,436,136),radius=12)
        p.text('GPU LOAD',(42,110),15,MUTED,center=False)
        p.text(f'{data.gpu_load_pct:.0f}%',(42,142),63,CYAN,center=False)
        fan(p,(366,158),43,self.angle)
        p.text(f'{data.gpu_fan_rpm:.0f} RPM',(366,213),16,AMBER)
        card(p,'GPU TEMPERATURE',f'{data.gpu_temp_c:.1f}','°C',22,248)
        card(p,'GPU BOARD POWER',f'{data.gpu_power_w:.0f}','W',251,248)
        load_bar(p,'VRAM',data.vram_used_gb/data.vram_total_gb*100,42,336,width=388)
        p.text(f'CPU FAN {data.cpu_fan_rpm:.0f} RPM',(42,405),17,TEXT,center=False)
        p.text(f'GPU FAN {data.gpu_fan_rpm:.0f} RPM',(268,405),17,TEXT,center=False)
        footer(p)
