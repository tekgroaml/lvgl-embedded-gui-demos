"""39s same-content scheduling, colorful scene models and true raster behavior."""
from dataclasses import asdict
import copy,json,math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from common.drawing import draw_scene
from demos.shared.cli import parser,command
from demos.different.round.playback import load_playlist,Timeline
from demos.same.round.playback import SameShowcaseSource,PLAYLIST,VIEWS,ICONS
from demos.same.round.panels import SamePanel
from scenes.same.round.ambient_light.model import LightDemo
from scenes.same.round.ambient_clock.model import ClockDemo
from scenes.registry import definition
from scene_app.config import normalize,prepare,load_layout
from scene_app.display import geometry
from scene_app.errors import AppError

try:
    import cairo
except ImportError:
    cairo=None


def request(**changes):
    return normalize({'port':1,'shape':'round','panels':2,'input':'none','content':'same',
                      'view':'product-showcase-same','layout':'product-showcase-same-clone-480',
                      'data_source':'demo',**changes})


class SameScheduleTests(unittest.TestCase):
    def test_three_intros_and_effects_have_exact_durations_and_repeat(self):
        s=SameShowcaseSource()
        self.assertEqual(s.timeline.cycle_seconds,39)
        for i,view in enumerate(VIEWS):
            for offset,phase in ((0,'intro'),(2.999,'intro'),(3,'effect'),(12.999,'effect')):
                d=s.read(13*i+offset)
                self.assertEqual((d.scene,d.phase,d.stage_index),(view,phase,i))
                self.assertEqual(d.phase_duration,3 if phase=='intro' else 10)
                self.assertTrue(d.simulated and d.payload.simulated)
        self.assertEqual(s.read(39).cycle_index,1)
        first=asdict(s.read(21).payload)
        self.assertEqual(asdict(s.read(60).payload),first)
        s.on_ready(100)
        self.assertEqual(s.read(102.999).phase,'intro')
        self.assertEqual(s.read(103).phase,'effect')

    def test_each_effect_changes_without_audio_processes(self):
        with patch('subprocess.run',side_effect=AssertionError('No audio')),\
             patch('subprocess.Popen',side_effect=AssertionError('No audio')):
            s=SameShowcaseSource()
            for index,field in enumerate(('bands','hue','second')):
                a=s.read(index*13+3).payload;b=s.read(index*13+11).payload
                self.assertNotEqual(getattr(a,field),getattr(b,field))
                self.assertIsNone(s.source.path)

    def test_cannot_insert_another_content_mode_or_live_scene(self):
        data,_=load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'playlist.json'
            for view in ('flight','product-showcase-same','unknown'):
                bad=copy.deepcopy(data);bad['stages'][0]['view']=view;p.write_text(json.dumps(bad))
                with self.assertRaises(AppError):load_playlist(p,views=VIEWS,icons=ICONS)
        fake=Mock(shapes=('round','round'),sources=('demo',),content_modes=('different',))
        with patch('scenes.registry.definition',return_value=fake):
            with self.assertRaises(AppError):SameShowcaseSource().read(0)

    def test_playlist_digest_and_wall_time_rules_are_retained(self):
        _,a,_=prepare(request())
        original=load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
        with patch('demos.same.round.playback.load_playlist',return_value=(original[0],'new-copy')):
            _,b,_=prepare(request())
        self.assertNotEqual(a,b)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fast.json';p.write_text('{"config_version":1,"demo_speed":2}')
            with self.assertRaises(AppError):prepare(request(config=str(p)))


class SameContractTests(unittest.TestCase):
    def test_default_wrapper_uses_hardware_clone_and_sbs_is_explicit(self):
        p=parser(fixed_shape=True,same_content=True)
        clone=command(p.parse_args(['start','--port','1']))
        self.assertIn('product-showcase-same',clone)
        self.assertIn('product-showcase-same-clone-480',clone)
        self.assertEqual(clone[clone.index('--content')+1],'same')
        sbs=command(p.parse_args(['start','--port','2','--signal','sbs','--size','800']))
        self.assertIn('product-showcase-same-sbs',sbs)
        self.assertIn('product-showcase-same-sbs-800',sbs)
        self.assertNotIn('--replace',sbs)
        self.assertEqual(command(p.parse_args(['restart','--port','1'])),['restart','--port','1'])
        old=command(parser().parse_args(['start','--port','1']))
        self.assertEqual(old[old.index('--content')+1],'different')

    def test_clone_and_sbs_signals_cannot_be_crossed(self):
        for kind in ('clone','sbs'):
            view='product-showcase-same' if kind=='clone' else 'product-showcase-same-sbs'
            for size in (480,720,800):
                layout=load_layout(f'product-showcase-same-{kind}-{size}')
                width=size if kind=='clone' else size*2
                output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                        'mode':{'width':width,'height':size,'refresh_hz':62.811001 if size==480 and kind=='clone' else 60}}
                self.assertEqual(geometry(output,layout),(0,0,width,size))
                spec=request(view=view,layout=layout['id'])
                self.assertEqual(spec['content'],'same')
                self.assertEqual(spec['topology'],layout['topology'])
                output['mode']['width']=size*2 if kind=='clone' else size
                with self.assertRaises(AppError):geometry(output,layout)
        for extra in ({'shape':'square'},{'content':'different'},{'data_source':'live'}):
            with self.assertRaises(AppError):request(**extra)

    def test_intros_are_same_and_effects_reuse_original_factories_without_time_skip(self):
        source=SameShowcaseSource();a,b=SamePanel(),SamePanel()
        for t in (0,13,26):
            data=source.read(t)
            with patch('demos.same.round.panels.icon') as icon,\
                 patch('demos.same.round.panels.fitted_text') as text:
                a.draw(Mock(),data);b.draw(Mock(),data)
                self.assertEqual(icon.call_count,2)
                self.assertEqual([c.args[1] for c in text.call_args_list],[data.title,data.subtitle]*2)
            effect=source.read(t+3)
            a.update(0,effect);b.update(0,effect)
            expected=definition(effect.scene).create_panels()[0]
            self.assertIs(type(a.panel),type(expected));self.assertIs(type(b.panel),type(expected))
            self.assertEqual(a.panel.frame.elapsed_s,effect.scene_elapsed)


class AmbientModelTests(unittest.TestCase):
    def test_lighting_is_bounded_smooth_and_repeatable(self):
        a,b=LightDemo(),LightDemo()
        for t in (0,4,10,100,1000):
            x=a.read(t);self.assertEqual(x,b.read(t))
            self.assertTrue(70<=x.brightness<=95 and 0<=x.hue<1)
            self.assertTrue(x.simulated and not x.stale)
            y=a.read(t+.01)
            self.assertLess(abs(y.brightness-x.brightness),.2)
        for bad in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):a.read(bad)

    def test_clock_seconds_rollover_and_day_wrap_are_valid(self):
        s=ClockDemo()
        for t in (0,59.9,60,1799.9,1800,41400,86400):
            d=s.read(t)
            self.assertTrue(0<=d.hour<24 and 0<=d.minute<60 and 0<=d.second<60)
            self.assertTrue(d.simulated and not d.stale)
        self.assertEqual((s.read(60).hour,s.read(60).minute),(12,31))
        self.assertEqual((s.read(41400).hour,s.read(41400).minute),(0,0))
        self.assertEqual(s.read(0).hour,s.read(86400).hour)
        self.assertIsNone(s.path)


@unittest.skipIf(cairo is None,'Real rendering needs Cairo')
class SameRasterTests(unittest.TestCase):
    def render(self,size,t,kind='sbs'):
        width=size*2 if kind=='sbs' else size
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,size)
        a,b=SamePanel(),SamePanel();d=SameShowcaseSource().read(t)
        a.update(0,d);b.update(0,d)
        draw_scene(cairo.Context(surface),load_layout(f'product-showcase-same-{kind}-{size}'),a,b,d)
        surface.flush();raw=bytes(surface.get_data());stride=surface.get_stride()
        left=b''.join(raw[y*stride:y*stride+size*4] for y in range(size))
        if kind=='sbs':
            right=b''.join(raw[y*stride+size*4:y*stride+size*8] for y in range(size))
            self.assertEqual(left,right)
        self.assertEqual(left[:3],b'\0\0\0')
        self.assertGreater(len(set(left)),100)
        return left

    def test_six_phases_match_on_all_sizes_and_both_board_topologies(self):
        for size in (480,720,800):
            for t in (0,8,13,21,26,34,39):
                with self.subTest(size=size,t=t):
                    self.assertEqual(self.render(size,t,'sbs'),self.render(size,t,'clone'))

    def test_each_effect_visibly_moves_and_has_bright_saturated_pixels(self):
        for start in (3,16,29):
            a=self.render(480,start);b=self.render(480,start+5)
            self.assertNotEqual(a,b)
            colorful=0
            for i in range(0,len(a),4):
                rgb=a[i:i+3]
                if max(rgb)>200 and max(rgb)-min(rgb)>120:colorful+=1
            self.assertGreater(colorful,4000,'Effects should include a substantial vivid region')


if __name__=='__main__':unittest.main()
