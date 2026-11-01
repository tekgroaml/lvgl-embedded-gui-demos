"""Deterministic 3s title + 10s effect playlist, using existing demo factories."""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

from common.simulation import validate_elapsed
from common.snapshots import read_snapshot
from scene_app.errors import AppError

PLAYLIST=Path(__file__).with_name('playlist.json')
VIEWS=('flight','automotive','pc-monitor')
ICONS={'flight':'aircraft','automotive':'vehicle','pc-monitor':'computer'}


def printable(value,maximum):
    return isinstance(value,str) and 1<=len(value)<=maximum and all(ord(c)>=32 for c in value)


def seconds(value,low,high):
    return type(value) in (int,float) and math.isfinite(value) and low<=value<=high


def load_playlist(path=PLAYLIST):
    try:
        data,_=read_snapshot(path)
        if (set(data)!={'playlist_version','intro_seconds','effect_seconds','stages'}
                or type(data['playlist_version']) is not int or data['playlist_version']!=1):
            raise ValueError()
        if not seconds(data['intro_seconds'],.2,600) or not seconds(data['effect_seconds'],.2,600):
            raise ValueError()
        stages=data['stages']
        if not isinstance(stages,list) or len(stages)!=3 or tuple(s['view'] for s in stages)!=VIEWS:
            raise ValueError()
        for stage in stages:
            if set(stage)!={'view','icon','title','subtitle','panel_labels','demo_start_seconds'}:raise ValueError()
            if stage['icon']!=ICONS[stage['view']]:raise ValueError()
            if not printable(stage['title'],24) or not printable(stage['subtitle'],36):raise ValueError()
            labels=stage['panel_labels']
            if not isinstance(labels,list) or len(labels)!=2 or not all(printable(v,28) for v in labels):raise ValueError()
            if not seconds(stage['demo_start_seconds'],0,600):raise ValueError()
        digest=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
        return data,digest
    except (OSError,ValueError,TypeError,KeyError):
        raise AppError('Invalid product showcase playlist. Check demos/product_showcase/playlist.json.',6) from None


@dataclass
class ShowcaseData:
    scene: str
    phase: str
    stage_index: int
    cycle_index: int
    stage_elapsed: float
    phase_elapsed: float
    phase_duration: float
    title: str
    subtitle: str
    panel_labels: tuple
    icon: str
    scene_elapsed: float
    payload: object
    stale: bool = False
    simulated: bool = True


class Timeline:
    def __init__(self,playlist):
        self.playlist=playlist
        self.stage_seconds=playlist['intro_seconds']+playlist['effect_seconds']
        self.cycle_seconds=len(playlist['stages'])*self.stage_seconds

    def locate(self,elapsed):
        validate_elapsed(elapsed)
        cycle=int(elapsed//self.cycle_seconds)
        position=elapsed-cycle*self.cycle_seconds
        index=min(len(self.playlist['stages'])-1,int(position//self.stage_seconds))
        within=position-index*self.stage_seconds
        intro=self.playlist['intro_seconds']
        if within<intro:return cycle,index,'intro',within,within,intro
        return cycle,index,'effect',within,within-intro,self.playlist['effect_seconds']


class ShowcaseSource:
    """Always simulation, with no subprocess switching, live files or sensors."""
    path=None
    requires_real_time=True

    def __init__(self):
        self.playlist,self.configuration_digest=load_playlist()
        self.timeline=Timeline(self.playlist)
        self.origin=0.
        self.current=None
        self.source=None
        self.last_elapsed=-1.

    def on_ready(self,elapsed):
        # The first title gets its full interval after its first visible frame.
        validate_elapsed(elapsed)
        self.origin=elapsed

    def read(self,elapsed):
        from scenes.registry import definition
        validate_elapsed(elapsed)
        shown=max(0.,elapsed-self.origin)
        cycle,index,phase,within,phase_elapsed,duration=self.timeline.locate(shown)
        token=(cycle,index)
        stage=self.playlist['stages'][index]
        if token!=self.current or shown<self.last_elapsed:
            scene=definition(stage['view'])
            if scene.shapes!=('round','round') or 'demo' not in scene.sources:
                raise AppError('The showcase requires the three declared round/round demo scenes.',3)
            self.source=scene.create_source('demo')
            self.current=token
        scene_elapsed=stage['demo_start_seconds']+(phase_elapsed if phase=='effect' else 0)
        sample=self.source.read(scene_elapsed)
        if not sample.simulated:raise AppError('Product showcase cannot display live data.',3)
        self.last_elapsed=shown
        return ShowcaseData(stage['view'],phase,index,cycle,within,phase_elapsed,duration,
                            stage['title'],stage['subtitle'],tuple(stage['panel_labels']),
                            stage['icon'],scene_elapsed,sample,stale=sample.stale)
