#!/usr/bin/env python3
"""Refresh generated scene capabilities from the authoritative scene registry.

Does not modify hardware acceptance evidence or global runtime settings.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_app import VERSION
from scenes.registry import DEFINITIONS


def update(data):
    scenes=tuple(DEFINITIONS.values())
    data['version']=VERSION
    data['views']=[{'id':scene.id,'data_sources':list(scene.sources)} for scene in scenes]
    data['layouts']=[scene.layout_path(size) for scene in scenes for size in scene.sizes]
    data['profiles']=[{
        'id':'sbs-'+scene.id,'topology':'single-link-dual','panel_count':2,
        'panels':[{'panel':i+1,'shape':shape,'input':'none','min_viewport':{'width':min(scene.sizes),'height':min(scene.sizes)}}
                  for i,shape in enumerate(scene.shapes)],
        'views':[scene.id],'data_sources':list(scene.sources),'content_modes':['different'],
        'layout_ids':[f'{scene.prefix}-{size}' for size in scene.sizes]
    } for scene in scenes]
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    path=Path(__file__).resolve().parents[1]/'screen-app.json'
    original=json.loads(path.read_text());generated=update(json.loads(path.read_text()))
    if args.check:
        if generated!=original:raise SystemExit('Manifest differs from scene registry. Run scripts/update_manifest.py.')
        print('Manifest matches scene registry.')
    else:
        path.write_text(json.dumps(generated,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
