"""Same-content routing, analytic beat simulation and real raster-copy regression."""
from dataclasses import asdict
import json
import math
from pathlib import Path
import unittest
from unittest.mock import Mock,patch

from common.drawing import draw_scene
from scene_app.config import normalize,load_layout,prepare
from scene_app.display import geometry
from scene_app.errors import AppError
from scenes.registry import DEFINITIONS,definition
from scenes.same.round.music_ambient.model import MusicDemo,sample,BPM,BANDS
from scenes.same.round.music_ambient.panels import MusicPanel

try:
    import cairo
except ImportError:
    cairo=None


def request(**changes):
    return normalize({'port':1,'shape':'round','panels':2,'input':'none',
                      'view':'music-ambient','layout':'music-ambient-sbs-480',
                      'content':'same','data_source':'demo',**changes})


class MusicContractTests(unittest.TestCase):
    def test_content_same_is_scene_specific_and_kept_in_saved_spec(self):
        value=request()
        self.assertEqual(value['content'],'same')
        inferred=dict(value);inferred.pop('view')
        self.assertEqual(normalize(inferred),value)
        for changes in ({'content':'different'},{'content':None},{'content':'unknown'},
                        {'shape':'square'},{'data_source':'live'},{'input':'touch'},
                        {'view':'flight'},{'layout':'flight-sbs-480'}):
            with self.subTest(changes=changes),self.assertRaises(AppError):request(**changes)
        for scene in DEFINITIONS.values():
            if 'same' in scene.content_modes:continue
            with self.subTest(scene=scene.id),self.assertRaises(AppError):
                normalize({'port':1,'shape':list(scene.shapes),'panels':2,'input':'none',
                           'view':scene.id,'layout':f'{scene.prefix}-480','content':'same'})

    def test_same_layout_metadata_cannot_be_changed_to_different(self):
        original=load_layout('music-ambient-sbs-480')
        original['content_mode']='different'
        with patch('scene_app.config.read_json',return_value=(original,'changed')):
            with self.assertRaises(AppError):load_layout('music-ambient-sbs-480')

    def test_sizes_and_refresh_validate_without_changing_display(self):
        for size in (480,720,800):
            layout=load_layout(f'music-ambient-sbs-{size}')
            self.assertEqual(layout['content_mode'],'same')
            self.assertEqual([p['view'] for p in layout['panels']],['music','music'])
            for rate in ([60,62.825001] if size==480 else [60]):
                output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                        'mode':{'width':size*2,'height':size,'refresh_hz':rate}}
                self.assertEqual(geometry(output,layout),(0,0,size*2,size))
                output['mode']['width']=size
                with self.assertRaises(AppError):geometry(output,layout)

    def test_manifest_advertises_same_only_for_the_new_profile(self):
        manifest=json.loads(Path('screen-app.json').read_text())
        self.assertEqual(set(manifest['content_modes']),{'same','different'})
        for profile in manifest['profiles']:
            self.assertEqual(profile['content_modes'],list(definition(profile['views'][0]).content_modes))

    def test_source_preparation_and_model_never_open_audio_or_launch_processes(self):
        with patch('subprocess.run',side_effect=AssertionError('No audio processes')),\
             patch('subprocess.Popen',side_effect=AssertionError('No audio processes')):
            _,_,source=prepare(request())
            self.assertIsInstance(source,MusicDemo)
            self.assertIsNone(source.path)
            for t in (0,3,90,500):self.assertTrue(source.read(t).simulated)


class MusicMotionTests(unittest.TestCase):
    def test_envelopes_and_progress_are_finite_bounded_and_deterministic(self):
        source=MusicDemo()
        for i in range(1801):
            data=source.read(i/10)
            self.assertEqual(len(data.bands),BANDS)
            self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in data.bands))
            self.assertTrue(0<=data.beat<=1 and 0<=data.breath<=1 and 0<=data.hue<1)
            self.assertTrue(0<=data.track_seconds<data.duration_seconds)
            self.assertTrue(data.simulated and not data.stale)
        source.read(900)
        self.assertEqual(asdict(source.read(2)),asdict(MusicDemo().read(2)))
        for bad in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):source.read(bad)

    def test_beat_attack_release_and_ambient_color_change(self):
        period=60/BPM
        peak=sample(period*4)
        release=sample(period*4.8)
        self.assertGreater(peak.beat,release.beat)
        self.assertNotEqual(peak.bands,release.bands)
        self.assertAlmostEqual(sample(8).breath,sample(0).breath)
        self.assertGreater(sample(4).breath,sample(0).breath)
        self.assertNotEqual(sample(0).hue,sample(30).hue)
        self.assertEqual(sample(90).track_seconds,0)

    def test_frame_state_matches_between_panels_and_advances_between_polls(self):
        a,b=definition('music-ambient').create_panels()
        data=sample(3)
        for _ in range(6):
            a.update(1/30,data);b.update(1/30,data)
            self.assertEqual(a.frame,b.frame)
        self.assertGreater(a.frame.elapsed_s,data.elapsed_s)
        before=a.frame
        a.update(1/30,sample(3.1))
        self.assertGreater(a.frame.elapsed_s,before.elapsed_s)


@unittest.skipIf(cairo is None,'Real rendering requires the existing Cairo runtime')
class MusicRasterTests(unittest.TestCase):
    def render(self,size,elapsed,readings=None):
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,size*2,size)
        a,b=definition('music-ambient').create_panels()
        data=sample(elapsed)
        if readings:
            for dt,t in readings:
                data=sample(t);a.update(dt,data);b.update(dt,data)
        # An intentionally different right view must never be drawn in same mode.
        b.draw=Mock(side_effect=AssertionError('Same mode must copy one raster'))
        draw_scene(cairo.Context(surface),load_layout(f'music-ambient-sbs-{size}'),a,b,data)
        surface.flush();pixels=bytes(surface.get_data());stride=surface.get_stride()
        left=b''.join(pixels[y*stride:y*stride+size*4] for y in range(size))
        right=b''.join(pixels[y*stride+size*4:y*stride+size*8] for y in range(size))
        self.assertEqual(left,right)
        self.assertEqual(left[:3],b'\0\0\0')
        self.assertGreater(len(set(left)),30,'A black/empty frame is not a successful copy')
        b.draw.assert_not_called()
        return left

    def test_all_sizes_have_pixel_identical_nonempty_circles_through_loop(self):
        for size in (480,720,800):
            for t in (0,3,45,89.9,90):
                with self.subTest(size=size,time=t):self.render(size,t)

    def test_visuals_animate_without_a_new_telemetry_sample(self):
        first=self.render(480,3,[(1/30,3)])
        later=self.render(480,3,[(1/30,3)]*6)
        self.assertNotEqual(first,later)

    def test_existing_different_content_path_still_draws_both_views(self):
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,960,480)
        left,right=Mock(),Mock()
        draw_scene(cairo.Context(surface),load_layout('flight-sbs-480'),left,right,Mock())
        left.draw.assert_called_once();right.draw.assert_called_once()

class HardwareCloneTests(unittest.TestCase):
    def test_actual_single_square_input_is_accepted_and_preserved(self):
        spec=request(view='music-ambient-clone',layout='music-ambient-clone-480')
        self.assertEqual(spec['topology'],'single-link-clone')
        self.assertEqual(spec['profile_id'],'clone-music-ambient-clone')
        layout=load_layout(spec['layout'])
        output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                'mode':{'width':480,'height':480,'refresh_hz':62.811001}}
        self.assertEqual(geometry(output,layout),(0,0,480,480))
        self.assertEqual(layout['panels'][0]['rect'],layout['panels'][1]['rect'])
        output['mode']['width']=960
        with self.assertRaises(AppError):geometry(output,layout)
        with self.assertRaises(AppError):request(view='music-ambient-clone',layout='music-ambient-clone-480',content='different')

    def test_clone_rectangles_cannot_be_silently_changed_to_sbs(self):
        layout=load_layout('music-ambient-clone-480')
        layout['panels'][1]['rect']['x']=480
        with patch('scene_app.config.read_json',return_value=(layout,'changed')):
            with self.assertRaises(AppError):load_layout('music-ambient-clone-480')

    def test_manifest_profiles_distinguish_sbs_from_hardware_duplication(self):
        manifest=json.loads(Path('screen-app.json').read_text())
        self.assertEqual(set(manifest['topologies']),{'single-link-dual','single-link-clone'})
        profile=next(p for p in manifest['profiles'] if p['views']==['music-ambient-clone'])
        self.assertEqual(profile['topology'],'single-link-clone')
        self.assertEqual(profile['panel_count'],2)

    @unittest.skipIf(cairo is None,'Real rendering requires the existing Cairo runtime')
    def test_hardware_clone_draws_one_circle_once_without_double_compositing(self):
        for size in (480,720,800):
            a,b=definition('music-ambient-clone').create_panels()
            data=sample(12)
            single=cairo.ImageSurface(cairo.FORMAT_ARGB32,size,size)
            sbs=cairo.ImageSurface(cairo.FORMAT_ARGB32,size*2,size)
            draw_scene(cairo.Context(single),load_layout(f'music-ambient-clone-{size}'),a,b,data)
            draw_scene(cairo.Context(sbs),load_layout(f'music-ambient-sbs-{size}'),a,b,data)
            single.flush();sbs.flush()
            raw=bytes(sbs.get_data());stride=sbs.get_stride()
            first=b''.join(raw[y*stride:y*stride+size*4] for y in range(size))
            self.assertEqual(bytes(single.get_data()),first)


if __name__=='__main__':unittest.main()
