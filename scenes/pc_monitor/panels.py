"""Round-safe CPU/memory and GPU/cooling pages for a PC case display."""
from common.theme import TEXT,MUTED,CYAN,AMBER,RED
from common.components import round_frame


def value(number,decimals=0,suffix=''):
    return '—' if number is None else f'{number:.{decimals}f}{suffix}'


def load_arc(p,load):
    for i in range(41):
        degrees=135+i/40*270
        active=load is not None and i/40*100<=load
        color=(RED if i>=36 else AMBER if i>=30 else CYAN) if active else (44,66,80)
        p.line(color,p.polar(202,degrees),p.polar(211 if i%5==0 else 207,degrees),3)
    p.text('0',(105,387),15,MUTED)
    p.text('100',(375,387),15,MUTED)


def footer(p,data):
    text='DEMO · SIMULATED PC' if data.simulated else 'OFFLINE · LAST PC DATA' if data.stale else 'LIVE · '+data.pc_name.upper()
    color=RED if data.stale else AMBER if data.simulated else CYAN
    p.text(text[:31],(240,423),12,color)


def meter(p,used,total,label_text,y):
    if used is None or total is None:
        p.text(label_text+'  —',(240,y),17,MUTED)
        return
    ratio=max(0,min(1,used/total))
    p.text(f'{label_text}  {used:.1f} / {total:g} GB',(240,y),17,TEXT)
    p.rect((37,56,70),(134,y+16,212,7),radius=3)
    if ratio>0:p.rect(AMBER if ratio>.85 else CYAN,(134,y+16,212*ratio,7),radius=3)


class CpuPanel:
    def update(self,dt,data):pass

    def draw(self,p,data,paused=False):
        round_frame(p,'CPU / MEMORY')
        load_arc(p,data.cpu_load_pct)
        p.text(data.workload[:24],(240,112),16,MUTED)
        p.text(value(data.cpu_load_pct,0,'%'),(240,182),66,TEXT)
        p.text('CPU UTILIZATION',(240,225),15,MUTED)
        p.text(value(data.cpu_temp_c,0,'°C'),(168,270),30,
               RED if data.cpu_temp_c is not None and data.cpu_temp_c>=85 else CYAN)
        p.text(value(data.cpu_power_w,0,' W'),(316,270),26,TEXT)
        p.text('TEMPERATURE',(168,298),12,MUTED)
        p.text('CPU POWER',(316,298),12,MUTED)
        meter(p,data.memory_used_gb,data.memory_total_gb,'RAM',337)
        p.text('CPU FAN  '+value(data.cpu_fan_rpm,0,' RPM'),(240,387),16,MUTED)
        footer(p,data)


class GpuPanel:
    def update(self,dt,data):pass

    def draw(self,p,data,paused=False):
        round_frame(p,'GPU / COOLING')
        load_arc(p,data.gpu_load_pct)
        p.text('GRAPHICS UTILIZATION',(240,112),15,MUTED)
        p.text(value(data.gpu_load_pct,0,'%'),(240,183),64,TEXT)
        p.text(value(data.gpu_temp_c,0,'°C'),(168,240),29,
               RED if data.gpu_temp_c is not None and data.gpu_temp_c>=85 else CYAN)
        p.text(value(data.gpu_power_w,0,' W'),(316,240),26,TEXT)
        p.text('GPU TEMP',(168,268),12,MUTED)
        p.text('GPU POWER',(316,268),12,MUTED)
        meter(p,data.vram_used_gb,data.vram_total_gb,'VRAM',307)
        p.text('GPU FAN  '+value(data.gpu_fan_rpm,0,' RPM'),(240,360),17,MUTED)
        p.text('NET DL '+value(data.download_mbps,1)+'  UL '+value(data.upload_mbps,1)+' Mbps',(240,389),14,MUTED)
        footer(p,data)
