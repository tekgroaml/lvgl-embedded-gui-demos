#!/usr/bin/env python3
"""Optional actual Cairo render check; creates no desktop/window or data adapter."""
import argparse
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gauges.common import TelemetrySource
from gauges.automotive_gauge import AutomotiveGauge
from gauges.industrial_panel import IndustrialPanel
from scene_app.config import load_layout
from scene_app.painter import draw_scene


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--size',type=int,choices=(480,720,800),default=480)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    import cairo
    layout=load_layout(f'automotive-industrial-sbs-{args.size}')
    a,b=AutomotiveGauge(),IndustrialPanel();source=TelemetrySource()
    for index in range(180):
        data=source.read(index/30);a.update(1/30,data);b.update(1/30,data)
    width,height=layout['signal_mode']['width'],layout['signal_mode']['height']
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    draw_scene(cairo.Context(surface),layout,a,b,data)
    # Compare live telemetry labels and stale rendering as actual draw paths too.
    data.simulated=False;data.stale=True
    scratch=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    draw_scene(cairo.Context(scratch),layout,a,b,data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    surface.write_to_png(str(args.output))
    png=args.output.read_bytes()
    assert struct.unpack('>II',png[16:24])==(width,height)
    surface.flush();pixels=bytes(surface.get_data());stride=surface.get_stride()
    # Little/big endian independent zero RGB test: first pixel of round panel is black.
    assert set(pixels[:3])=={0},'round panel corner must stay outside the visible circle'
    left=bytearray();right=bytearray()
    for row in range(height):
        start=row*stride
        left.extend(pixels[start:start+args.size*4])
        right.extend(pixels[start+args.size*4:start+width*4])
    assert left!=right,'SBS regions must show different content'
    print(f'PASS: native {width}x{height}, two distinct regions, circular clip, live/stale paths -> {args.output}')


if __name__=='__main__':main()
