"""Exact product-demo scheduling and safe reuse of existing scene factories."""
from dataclasses import asdict
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from demos.different.round.cli import command,parser
from demos.different.round.playback import Timeline,ShowcaseSource,load_playlist
from demos.different.round.panels import LeftPanel,RightPanel
from scene_app.config import normalize,prepare,load_layout
from scene_app.display import geometry
from scene_app.worker import Worker
from scene_app.errors import AppError
from scenes.registry import definition


def request(**changes):
    return normalize({'port':1,'shape':'round','panels':2,'input':'none','view':'product-showcase',
                      'layout':'product-showcase-sbs-480','content':'different',**changes})


class ScheduleTests(unittest.TestCase):
    def test_exact_three_second_titles_and_ten_second_effects(self):
        data,_=load_playlist();timeline=Timeline(data)
        self.assertEqual(timeline.cycle_seconds,39)
        for start,index in ((0,0),(13,1),(26,2)):
            self.assertEqual(timeline.locate(start)[1:3],(index,'intro'))
            self.assertEqual(timeline.locate(start+2.999)[1:3],(index,'intro'))
            self.assertEqual(timeline.locate(start+3)[1:3],(index,'effect'))
            self.assertAlmostEqual(timeline.locate(start+3)[4],0)
            self.assertEqual(timeline.locate(start+12.999)[1:3],(index,'effect'))
        self.assertEqual(timeline.locate(39)[:3],(1,0,'intro'))
        self.assertEqual(timeline.locate(39*100+16)[:3],(100,1,'effect'))

    def test_order_and_each_scene_snapshot_have_separate_schemas(self):
        source=ShowcaseSource()
        expected=((3,'flight','airspeed_kt'),(16,'automotive','speed_kmh'),(29,'pc-monitor','cpu_load_pct'))
        for time,view,key in expected:
            sample=source.read(time)
            self.assertEqual(sample.scene,view)
            self.assertEqual(sample.phase,'effect')
            self.assertIn(key,asdict(sample.payload))
            self.assertTrue(sample.simulated and sample.payload.simulated)
            self.assertFalse(sample.stale)

    def test_first_visible_title_gets_its_full_duration(self):
        source=ShowcaseSource()
        source.read(.4)
        source.on_ready(.5)
        self.assertEqual(source.read(.5).phase,'intro')
        self.assertEqual(source.read(3.499).phase,'intro')
        self.assertEqual(source.read(3.5).phase,'effect')
        self.assertEqual(source.read(13.5).scene,'automotive')
        self.assertEqual(source.read(13.5).phase,'intro')

    def test_active_seed_offsets_keep_short_effects_from_starting_idle(self):
        source=ShowcaseSource()
        car=source.read(16).payload
        self.assertEqual(car.phase,'ACCELERATING');self.assertGreater(car.speed_kmh,20)
        pc=source.read(29).payload
        self.assertGreater(pc.cpu_load_pct+pc.gpu_load_pct,100)
        early=source.read(3).payload;later=source.read(7).payload
        self.assertGreater(later.altitude_ft,early.altitude_ft)
        self.assertNotEqual(later.heading_deg,early.heading_deg)

    def test_sources_reset_per_cycle_and_seeking_back_does_not_leak_previous_values(self):
        source=ShowcaseSource()
        first=asdict(source.read(18).payload)
        source.read(38)
        next_cycle=asdict(source.read(57).payload)
        self.assertEqual(first,next_cycle)
        source.read(200)
        self.assertEqual(first,asdict(source.read(18).payload))
        for bad in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):source.read(bad)

    def test_no_real_data_or_child_process_switching(self):
        with patch('subprocess.run',side_effect=AssertionError('Do not launch scene processes')),\
             patch('subprocess.Popen',side_effect=AssertionError('Do not launch scene processes')):
            source=ShowcaseSource()
            for time in (0,3,13,16,26,29,39,42):
                sample=source.read(time)
                self.assertTrue(sample.simulated and sample.payload.simulated)
                self.assertIsNone(source.source.path)


class PlaylistTests(unittest.TestCase):
    def test_custom_copy_can_edit_copy_and_durations_without_shell_commands(self):
        data,digest=load_playlist()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'playlist.json'
            data['stages'][0]['title']='FLIGHT INSTRUMENTS'
            data['intro_seconds']=4
            path.write_text(json.dumps(data))
            custom,new_digest=load_playlist(path)
            self.assertNotEqual(digest,new_digest)
            self.assertEqual(Timeline(custom).cycle_seconds,42)

    def test_invalid_playlist_is_a_configuration_error(self):
        base,_=load_playlist()
        changes=[lambda d:d.update(intro_seconds=0),lambda d:d.update(effect_seconds=True),
                 lambda d:d.update(effect_seconds=float('nan')),lambda d:d.update(stages=[]),
                 lambda d:d['stages'][0].update(view='product-showcase'),
                 lambda d:d['stages'][0].update(demo_start_seconds=-1),
                 lambda d:d['stages'][0].update(icon='remote-url'),
                 lambda d:d['stages'][0].update(title='bad\ncaption'),
                 lambda d:d['stages'][0].update(shell='command')]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'playlist.json'
            for change in changes:
                data=copy.deepcopy(base);change(data);path.write_text(json.dumps(data))
                with self.subTest(data=data),self.assertRaises(AppError) as error:load_playlist(path)
                self.assertEqual(error.exception.code,6)

    def test_global_demo_speed_cannot_silently_change_product_video_timing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json';path.write_text('{"config_version":1,"demo_speed":2}')
            with self.assertRaises(AppError) as error:prepare(request(config=str(path)))
            self.assertEqual(error.exception.code,6)

    def test_playlist_changes_participate_in_idempotent_instance_digest(self):
        _,first,_=prepare(request())
        original=load_playlist()
        with patch('demos.different.round.playback.load_playlist',return_value=(original[0],'different-copy')):
            _,second,_=prepare(request())
        self.assertNotEqual(first,second)


class RenderingAndCommandTests(unittest.TestCase):
    def test_intro_assigns_brand_icon_to_left_and_application_copy_to_right(self):
        source=ShowcaseSource()
        for elapsed in (0,13,26):
            data=source.read(elapsed)
            left_painter,right_painter=Mock(),Mock()
            with patch('demos.shared.panels.fitted_text') as fitted,\
                 patch('demos.shared.panels.draw_icon') as icon:
                LeftPanel().draw(left_painter,data)
                icon.assert_called_once_with(left_painter,data.icon)
                texts=[call.args[1] for call in fitted.call_args_list]
                self.assertIn('TEKGROAML',texts)
                self.assertNotIn(data.title,texts)
                icon.reset_mock();fitted.reset_mock()
                RightPanel().draw(right_painter,data)
                icon.assert_not_called()
                texts=[call.args[1] for call in fitted.call_args_list]
                self.assertIn(data.title,texts)
                self.assertIn(data.subtitle,texts)
                self.assertIn(data.panel_labels[0],texts)
                self.assertIn(data.panel_labels[1],texts)
                self.assertNotIn('TEKGROAML',texts)

    def test_effect_panels_are_real_original_panels_and_reset_between_cycles(self):
        source=ShowcaseSource();left,right=LeftPanel(),RightPanel()
        for time,view in ((3,'flight'),(16,'automotive'),(29,'pc-monitor')):
            sample=source.read(time)
            left.update(1/30,sample);right.update(1/30,sample)
            expected=definition(view).create_panels()
            self.assertIs(type(left.panel),type(expected[0]))
            self.assertIs(type(right.panel),type(expected[1]))
        old=left.panel
        left.update(1/30,source.read(68))
        self.assertIsNot(left.panel,old)

    def test_wrapper_forwards_standard_lifecycle_and_does_not_stop_other_apps(self):
        args=parser().parse_args(['start','--port','2','--size','800'])
        values=command(args)
        self.assertEqual(values[:3],['start','--port','2'])
        self.assertEqual(values[values.index('--view')+1],'product-showcase')
        self.assertIn('product-showcase-sbs-800',values)
        self.assertNotIn('--replace',values)
        self.assertEqual(command(parser().parse_args(['stop','--port','1'])),['stop','--port','1'])
        self.assertEqual(command(parser().parse_args(['logs','--port','1','--follow'])),['logs','--port','1','--follow'])

    def test_registered_layout_accepts_current_dual480_rate_and_rejects_live(self):
        output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                'mode':{'width':960,'height':480,'refresh_hz':62.825001}}
        self.assertEqual(geometry(output,load_layout('product-showcase-sbs-480')),(0,0,960,480))
        self.assertTrue(definition('product-showcase').layout_path(480).startswith('demos/different/round/'))
        with self.assertRaises(AppError):request(data_source='live')

    def test_worker_status_exposes_stage_and_phase_for_ssh_observation(self):
        worker=Worker(request());worker.persist=Mock();worker.mark_ready=Mock()
        worker.received(ShowcaseSource().read(16),False)
        self.assertEqual(worker.state['telemetry']['scene'],'automotive')
        self.assertEqual(worker.state['telemetry']['phase'],'effect')
        self.assertEqual(worker.state['telemetry']['phase_duration'],10)
        self.assertTrue(worker.state['telemetry']['payload']['simulated'])

    def test_worker_anchors_presentation_clock_once_after_first_verified_frame(self):
        worker=Worker(request())
        worker.source=ShowcaseSource()
        worker.drawn=worker.has_data=True
        worker.begin=100.
        worker.state['viewport']={'width':960,'height':480}
        worker.persist=Mock();worker.event=Mock();worker.verify_surface=Mock(return_value=True)
        with patch('scene_app.worker.time.monotonic',return_value=102.):worker.mark_ready()
        self.assertTrue(worker.ready)
        self.assertEqual(worker.source.origin,2.)
        self.assertEqual(worker.source.read(4.999).phase,'intro')
        self.assertEqual(worker.source.read(5).phase,'effect')
        with patch('scene_app.worker.time.monotonic',return_value=110.):worker.mark_ready()
        self.assertEqual(worker.source.origin,2.,'health/data callbacks must not restart the title clock')


if __name__=='__main__':unittest.main()
