"""Physical code grouping, legacy identity, square business logic and four scripts."""
from dataclasses import asdict
import importlib,json
from pathlib import Path
import subprocess,sys
import unittest
from unittest.mock import patch

from common.drawing import draw_scene
from demos.shared.cli import parser,command
from demos.shared.playback import load_playlist
from demos.same.square.playback import SquareSameSource,PLAYLIST,VIEWS,ICONS
from demos.same.square.panels import SquareSamePanel
from demos.same.round.playback import VIEWS as ROUND_VIEWS
from scenes.registry import DEFINITIONS,definition,make_scene
from scene_app.config import normalize,load_layout,prepare
from scene_app.display import geometry
from scene_app.errors import AppError
from scenes.same.square.store_signage.model import StoreDemo
from scenes.same.square.meeting_room.model import RoomDemo
from scenes.same.square.parcel_status.model import ParcelDemo

try:
 import cairo
except ImportError:
 cairo=None


def request(**changes):
 return normalize({'port':1,'shape':'square','panels':2,'input':'none','content':'same',
                   'view':'product-showcase-same-square','layout':'product-showcase-same-square-clone-480',
                   'data_source':'demo',**changes})


class GroupArchitectureTests(unittest.TestCase):
 def test_every_implementation_is_owned_by_its_content_group(self):
  for scene in DEFINITIONS.values():
   mode=scene.content_modes[0]
   with self.subTest(scene=scene.id):
    package=scene.owner_package
    self.assertTrue(package.startswith(('scenes.'+mode+'.','demos.'+mode+'.')),package)
    for ref in (*scene.panel_factories,scene.demo_factory):
     self.assertTrue(ref.startswith(package+'.'),ref)
    for size in scene.sizes:
     self.assertTrue(scene.layout_path(size).startswith(package.replace('.','/')+'/layouts/'))
  for p in list(Path('scenes/same').rglob('*.py'))+list(Path('demos/same').rglob('*.py')):
   text=p.read_text()
   self.assertNotIn('from scenes.different.',text)
   self.assertNotIn('from demos.different.',text)

 def test_legacy_imports_export_the_same_classes_and_layouts_are_not_duplicated(self):
  for old,new,name in (
   ('scenes.automotive.model','scenes.different.automotive.model','AutomotiveDemo'),
   ('scenes.flight.model','scenes.different.flight.model','FlightDemo'),
   ('scenes.music_ambient.model','scenes.same.round.music_ambient.model','MusicDemo'),
   ('demos.same_showcase.playback','demos.same.round.playback','SameShowcaseSource'),
   ('demos.product_showcase.playback','demos.different.round.playback','ShowcaseSource')):
    self.assertIs(getattr(importlib.import_module(old),name),getattr(importlib.import_module(new),name))
    self.assertFalse((Path(old.rsplit('.',1)[0].replace('.','/'))/'layouts').exists())

 def test_canonical_and_legacy_commands_work_from_another_directory(self):
  root=Path.cwd()
  for entry in ('demos/different/round/demo','demos/different/square/demo',
                'demos/same/round/demo','demos/same/square/demo',
                'demos/product_showcase/demo','demos/square_showcase/demo','demos/same_showcase/demo'):
   result=subprocess.run([str(root/entry),'--version'],cwd='/tmp',capture_output=True,text=True,timeout=10)
   self.assertEqual(result.returncode,0,(entry,result.stderr))
   from scene_app import VERSION
   self.assertEqual(result.stdout.strip(),VERSION)

 def test_four_command_families_keep_distinct_views_and_shapes(self):
  configs=(('different','round','product-showcase'),('different','square','product-showcase-square'),
           ('same','round','product-showcase-same'),('same','square','product-showcase-same-square'))
  for mode,shape,view in configs:
   args=parser(default_shape=shape,fixed_shape=True,same_content=mode=='same').parse_args(['start','--port','1'])
   cmd=command(args)
   self.assertEqual(cmd[cmd.index('--view')+1],view)
   self.assertEqual(cmd[cmd.index('--shape')+1],shape)
   self.assertEqual(cmd[cmd.index('--content')+1],mode)
   if mode=='same':
    args=parser(default_shape=shape,fixed_shape=True,same_content=True).parse_args(['start','--port','2','--signal','sbs'])
    self.assertIn(view+'-sbs',command(args))


class SquareSameBehaviorTests(unittest.TestCase):
 def test_lineup_is_distinct_from_round_and_time_boundaries_are_exact(self):
  self.assertFalse(set(VIEWS)&set(ROUND_VIEWS))
  s=SquareSameSource()
  self.assertEqual(s.timeline.cycle_seconds,39)
  for i,view in enumerate(VIEWS):
   for offset,phase in ((0,'intro'),(2.999,'intro'),(3,'effect'),(12.999,'effect')):
    d=s.read(i*13+offset)
    self.assertEqual((d.scene,d.phase),(view,phase))
    self.assertEqual(d.phase_duration,3 if phase=='intro' else 10)
    self.assertTrue(d.simulated and d.payload.simulated)
  self.assertEqual(s.read(39).cycle_index,1)
  before=asdict(s.read(21).payload)
  self.assertEqual(asdict(s.read(60).payload),before)
  s.on_ready(100)
  self.assertEqual(s.read(102.999).phase,'intro')
  self.assertEqual(s.read(103).phase,'effect')

 def test_offers_booking_and_shipment_actually_change_during_each_effect(self):
  s=SquareSameSource()
  for start,field in ((3,'product'),(16,'status'),(29,'status')):
   self.assertNotEqual(getattr(s.read(start).payload,field),getattr(s.read(start+9).payload,field))
  for source in (StoreDemo(),RoomDemo(),ParcelDemo()):
   self.assertIsNone(source.path)
   for i in range(150):
    data=source.read(i*.7)
    self.assertTrue(data.simulated and not data.stale)
    for key,value in asdict(data).items():
     if 'progress' in key:self.assertTrue(0<=value<1)
   for t in (-1,float('nan'),float('inf')):
    with self.assertRaises(ValueError):source.read(t)
   self.assertEqual(source.read(4),type(source)().read(4))

 def test_shapes_content_and_input_modes_are_strict(self):
  for kind in ('clone','sbs'):
   view='product-showcase-same-square'+('-sbs' if kind=='sbs' else '')
   for size in (480,720,800):
    layout=load_layout(f'product-showcase-same-square-{kind}-{size}')
    spec=request(view=view,layout=layout['id'])
    output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
            'mode':{'width':size*(2 if kind=='sbs' else 1),'height':size,'refresh_hz':60}}
    self.assertEqual(geometry(output,layout),(0,0,output['mode']['width'],size))
    self.assertEqual(spec['shape'],['square','square'])
    output['mode']['refresh_hz']=62.811001
    if kind=='clone' and size==480:
     self.assertEqual(geometry(output,layout),(0,0,size,size))
     self.assertEqual(layout['version'],'1.1.0')
    else:
     with self.assertRaises(AppError):geometry(output,layout)
  for change in ({'shape':'round'},{'content':'different'},{'data_source':'live'},
                 {'layout':'product-showcase-same-clone-480'}):
   with self.assertRaises(AppError):request(**change)

 def test_source_cannot_use_real_data_or_different_content(self):
  original=load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
  with patch('subprocess.Popen',side_effect=AssertionError('No external sources')):
   for t in (0,3,13,16,26,29):self.assertTrue(SquareSameSource().read(t).simulated)
  _,digest,_=prepare(request())
  with patch('demos.same.square.playback.load_playlist',return_value=(original[0],'new-copy')):
   self.assertNotEqual(prepare(request())[1],digest)


@unittest.skipIf(cairo is None,'Actual rendering needs Cairo')
class SquareSameRasterTests(unittest.TestCase):
 def render(self,size,t,kind):
  d=SquareSameSource().read(t);a,b=SquareSamePanel(),SquareSamePanel()
  a.update(0,d);b.update(0,d)
  width=size*(2 if kind=='sbs' else 1)
  surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,size)
  draw_scene(cairo.Context(surface),load_layout(f'product-showcase-same-square-{kind}-{size}'),a,b,d)
  surface.flush();raw=bytes(surface.get_data());stride=surface.get_stride()
  left=b''.join(raw[y*stride:y*stride+size*4] for y in range(size))
  if kind=='sbs':self.assertEqual(left,b''.join(raw[y*stride+size*4:y*stride+size*8] for y in range(size)))
  self.assertTrue(any(left[:3]),'Square corners must remain usable')
  self.assertGreater(len(set(left)),100)
  return left

 def test_all_six_phases_and_loop_on_three_sizes_and_both_board_types(self):
  for size in (480,720,800):
   for t in (0,8,13,21,26,34,39):
    with self.subTest(size=size,time=t):
     self.assertEqual(self.render(size,t,'clone'),self.render(size,t,'sbs'))

 def test_effects_and_intros_are_visibly_active(self):
  for start in (0,3,13,16,26,29):
   self.assertNotEqual(self.render(480,start,'clone'),self.render(480,start+2,'clone'))


if __name__=='__main__':unittest.main()
