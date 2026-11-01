#!/usr/bin/env python3
"""Actual Cairo render check, without a desktop window or real data source."""
import argparse
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scenes.registry import make_scene
from scene_app.config import load_layout,SCENES
from common.drawing import draw_scene


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--size',type=int,choices=(480,720,800),default=480)
    p.add_argument('--view',choices=tuple(SCENES),default='automotive-industrial')
    p.add_argument('--elapsed',type=float,default=50)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not 0<=args.elapsed<=3600:p.error('Use --elapsed 0..3600 seconds.')
    import cairo
    layout=load_layout(f"{SCENES[args.view]['prefix']}-{args.size}")
    (a,b),source=make_scene(args.view)
    data=source.read(0)
    frames=round(args.elapsed*30)
    for index in range(frames):
        data=source.read((index+1)/30);a.update(1/30,data);b.update(1/30,data)
    width,height=layout['signal_mode']['width'],layout['signal_mode']['height']
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    draw_scene(cairo.Context(surface),layout,a,b,data)
    if args.view=='automotive-industrial':
        data.simulated=False;data.stale=True
        scratch=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
        draw_scene(cairo.Context(scratch),layout,a,b,data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    surface.write_to_png(str(args.output))
    png=args.output.read_bytes()
    assert struct.unpack('>II',png[16:24])==(width,height)
    surface.flush();pixels=bytes(surface.get_data());stride=surface.get_stride()
    for panel in layout['panels']:
        start=panel['rect']['x']*4
        corner=pixels[start:start+3]
        if panel['shape']=='round':assert set(corner)=={0},'circular panel corners must be black'
        else:assert any(corner),'square panel corners remain usable'
    left=bytearray();right=bytearray()
    for row in range(height):
        start=row*stride
        left.extend(pixels[start:start+args.size*4])
        right.extend(pixels[start+args.size*4:start+width*4])
    assert left!=right,'SBS regions must show different content'
    print(f'PASS: {args.view}, {width}x{height}, two distinct panels with correct masks -> {args.output}')


if __name__=='__main__':main()
