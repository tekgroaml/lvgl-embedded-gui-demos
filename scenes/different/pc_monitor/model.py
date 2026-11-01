"""PC-case showroom model and bounded, explicit remote-PC JSON telemetry."""
from dataclasses import dataclass
import math
import time

from common.simulation import smooth,validate_elapsed
from common.snapshots import read_snapshot


@dataclass
class PcData:
    pc_name: str = 'PC TELEMETRY'
    workload: str = 'WAITING FOR DATA'
    cpu_load_pct: float = None
    cpu_temp_c: float = None
    cpu_power_w: float = None
    memory_used_gb: float = None
    memory_total_gb: float = None
    gpu_load_pct: float = None
    gpu_temp_c: float = None
    gpu_power_w: float = None
    vram_used_gb: float = None
    vram_total_gb: float = None
    cpu_fan_rpm: float = None
    gpu_fan_rpm: float = None
    download_mbps: float = None
    upload_mbps: float = None
    elapsed_s: float = 0.
    sampled_at: float = None
    stale: bool = False
    simulated: bool = True


def targets(elapsed):
    """Smooth transitions between idle, CPU render, gaming, and cooling."""
    t=elapsed%180
    if t<15:return 7.,3.,'IDLE'
    if t<30:
        u=smooth((t-15)/15);return 7+81*u,3+9*u,'CPU RENDER'
    if t<60:return 88+4*math.sin((t-30)*math.pi/30)**2,12.,'CPU RENDER'
    if t<75:
        u=smooth((t-60)/15);return 88-42*u,12+83*u,'GAMING'
    if t<120:return 46+8*math.sin((t-75)*math.pi/45)**2,95.,'GAMING'
    if t<140:
        u=smooth((t-120)/20);return 46-39*u,95-92*u,'COOLING'
    return 7.,3.,'COOLING'


class PcDemo:
    """No local host sensors are queried: these are clearly marked simulated PCs."""
    path=None
    def __init__(self):
        self.last_time=0.
        self.cpu_temp=34.;self.gpu_temp=32.
        self.cpu_fan=720.;self.gpu_fan=0.

    def read(self,elapsed):
        validate_elapsed(elapsed)
        if elapsed<self.last_time:self.__init__()
        while self.last_time<elapsed-1e-9:
            dt=min(.1,elapsed-self.last_time);now=self.last_time+dt
            cpu,gpu,_=targets(now)
            self.cpu_temp+=(31+cpu*.55-self.cpu_temp)*(1-math.exp(-dt/12))
            self.gpu_temp+=(30+gpu*.52-self.gpu_temp)*(1-math.exp(-dt/18))
            cpu_fan=650+max(0,self.cpu_temp-32)*26
            gpu_fan=0 if self.gpu_temp<42 else 600+(self.gpu_temp-42)*28
            self.cpu_fan+=(cpu_fan-self.cpu_fan)*(1-math.exp(-dt/4))
            self.gpu_fan+=(gpu_fan-self.gpu_fan)*(1-math.exp(-dt/5))
            self.last_time=now
        cpu,gpu,phase=targets(elapsed)
        memory=7+cpu*.045+gpu*.035
        return PcData(pc_name='DEMO PC',workload=phase,
                      cpu_load_pct=cpu,cpu_temp_c=self.cpu_temp,cpu_power_w=14+cpu*1.15,
                      memory_used_gb=memory,memory_total_gb=32,
                      gpu_load_pct=gpu,gpu_temp_c=self.gpu_temp,gpu_power_w=16+gpu*2.5,
                      vram_used_gb=.7+gpu*.085,vram_total_gb=12,
                      cpu_fan_rpm=self.cpu_fan,gpu_fan_rpm=self.gpu_fan,
                      download_mbps=.4+gpu*.055,upload_mbps=.15+gpu*.008,
                      elapsed_s=elapsed,stale=False,simulated=True)


OPTIONAL_LIMITS={
    'cpu_temp_c':(-20,150),'gpu_temp_c':(-20,150),
    'cpu_power_w':(0,2000),'gpu_power_w':(0,3000),
    'gpu_load_pct':(0,100),'vram_used_gb':(0,2048),'vram_total_gb':(.01,2048),
    'cpu_fan_rpm':(0,30000),'gpu_fan_rpm':(0,30000),
    'download_mbps':(0,1000000),'upload_mbps':(0,1000000),
}


def number(value,low,high):
    if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:
        raise ValueError('Invalid PC metric')
    return float(value)


def label(value,maximum=32):
    if not isinstance(value,str) or not 1<=len(value)<=maximum or any(ord(c)<32 for c in value):
        raise ValueError('Invalid PC label')
    return value


def decode_snapshot(data,now):
    if type(data.get('schema_version')) is not int or data['schema_version']!=1:
        raise ValueError('Unknown PC telemetry schema')
    timestamp=number(data['sampled_at'],0,1e12)
    name=label(data['pc_name'])
    cpu=number(data['cpu_load_pct'],0,100)
    used=number(data['memory_used_gb'],0,65536)
    total=number(data['memory_total_gb'],.01,65536)
    if used>total:raise ValueError('Memory usage exceeds capacity')
    values={name:None if data.get(name) is None else number(data[name],*limits)
            for name,limits in OPTIONAL_LIMITS.items()}
    # VRAM must be supplied as a complete pair, otherwise it is unavailable.
    if (values['vram_used_gb'] is None)!=(values['vram_total_gb'] is None):
        raise ValueError('Incomplete VRAM capacity')
    if values['vram_used_gb'] is not None and values['vram_used_gb']>values['vram_total_gb']:
        raise ValueError('VRAM usage exceeds capacity')
    return PcData(pc_name=name,workload=label(data.get('workload','LIVE PC'),24),
                  cpu_load_pct=cpu,memory_used_gb=used,memory_total_gb=total,
                  sampled_at=timestamp,stale=not -2<=now-timestamp<=5,simulated=False,**values)


class PcJsonSource:
    """Reads a snapshot produced on the monitored PC, never the Pi's own stats."""
    def __init__(self,path):
        if path is None:raise ValueError('A PC snapshot path is required')
        self.path=path;self.last_poll=-1.
        self.last=PcData(stale=True,simulated=False)

    def read(self,elapsed):
        if elapsed-self.last_poll<.2:
            if self.last.sampled_at is not None:
                self.last.stale=self.last.stale or not -2<=time.time()-self.last.sampled_at<=5
            return self.last
        self.last_poll=elapsed
        try:
            data,_=read_snapshot(self.path)
            sample=decode_snapshot(data,time.time())
            # Old but structurally valid snapshots cannot replace newer readings.
            if sample.stale:
                self.last.stale=True
            elif self.last.sampled_at is not None and sample.sampled_at<self.last.sampled_at:
                # Do not roll metrics back if a delayed upload is still inside
                # the freshness window. Retain the newest sample's health.
                self.last.stale=self.last.stale or not -2<=time.time()-self.last.sampled_at<=5
            else:
                self.last=sample
        except (OSError,ValueError,KeyError,TypeError):
            self.last.stale=True;self.last.simulated=False
        return self.last
