"""Square presentation timing, physical geometry and coherent simulated metrics."""
from dataclasses import asdict
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from common.square import History
from demos.product_showcase.cli import parser,command
from demos.product_showcase.playback import ShowcaseSource,Timeline,load_playlist
from demos.square_showcase.playback import SquareShowcaseSource,PLAYLIST,VIEWS,ICONS
from demos.square_showcase.panels import LeftPanel,RightPanel
from scene_app.config import normalize,prepare,load_layout
from scene_app.display import geometry
from scene_app.errors import AppError
from scenes.registry import definition
from scenes.smart_home.model import HomeDemo
from scenes.pc_monitor.model import PcDemo
from scenes.pc_monitor_square.model import PcSquareDemo


def request(**changes):
    return normalize({'port':1,'shape':'square','panels':2,'input':'none',
                      'view':'product-showcase-square','layout':'product-showcase-square-sbs-480',
                      'content':'different',**changes})


class SquarePlaybackTests(unittest.TestCase):
    def test_all_six_phases_then_next_loop_preserve_three_and_ten_seconds(self):
        source=SquareShowcaseSource()
        self.assertEqual(source.timeline.cycle_seconds,39)
        for i,view in enumerate(VIEWS):
            for offset,phase in ((0,'intro'),(2.999,'intro'),(3,'effect'),(12.999,'effect')):
                data=source.read(i*13+offset)
                self.assertEqual((data.scene,data.phase,data.stage_index),(view,phase,i))
                self.assertEqual(data.phase_duration,3 if phase=='intro' else 10)
                self.assertTrue(data.simulated and data.payload.simulated)
        self.assertEqual(source.read(39).cycle_index,1)
        source.on_ready(40)
        self.assertEqual(source.read(42.999).phase,'intro')
        self.assertEqual(source.read(43).phase,'effect')

    def test_active_effects_change_both_panels_metrics(self):
        source=SquareShowcaseSource()
        fields=(('temperature_c','solar_w'),('cpu_load_pct','gpu_load_pct'),('rpm','pressure_bar'))
        for i,names in enumerate(fields):
            a=source.read(i*13+3).payload;b=source.read(i*13+11).payload
            for name in names:self.assertNotAlmostEqual(getattr(a,name),getattr(b,name),places=2)
            if i==2:self.assertGreater(b.produced_liters,a.produced_liters)

    def test_backwards_seek_and_new_loop_reset_sources(self):
        source=SquareShowcaseSource()
        first=asdict(source.read(18).payload)
        source.read(38)
        self.assertEqual(asdict(source.read(57).payload),first)
        source.read(80)
        self.assertEqual(asdict(source.read(18).payload),first)

    def test_round_and_square_playlists_cannot_cross_or_recurse(self):
        data,_=load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
        with self.assertRaises(AppError):load_playlist(PLAYLIST)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'playlist.json'
            for view in ('product-showcase-square','flight','unknown'):
                bad=copy.deepcopy(data);bad['stages'][0]['view']=view;path.write_text(json.dumps(bad))
                with self.assertRaises(AppError):load_playlist(path,views=VIEWS,icons=ICONS)
        self.assertEqual(ShowcaseSource().read(3).scene,'flight')

    def test_intro_split_and_square_frames_and_real_scene_factories(self):
        source=SquareShowcaseSource()
        for t in (0,13,26):
            data=source.read(t);left,right=LeftPanel(),RightPanel()
            with patch('demos.product_showcase.panels.fitted_text') as fitted,\
                 patch('demos.product_showcase.panels.draw_icon') as icon,\
                 patch('demos.product_showcase.panels.round_frame') as circle:
                left.draw(Mock(),data)
                self.assertIn('TEKGROAML',[c.args[1] for c in fitted.call_args_list])
                icon.assert_called_once();circle.assert_not_called()
                fitted.reset_mock();icon.reset_mock()
                right.draw(Mock(),data)
                self.assertIn(data.title,[c.args[1] for c in fitted.call_args_list])
                icon.assert_not_called();circle.assert_not_called()
            effect=source.read(t+3)
            left.update(.1,effect);right.update(.1,effect)
            a,b=definition(data.scene).create_panels()
            self.assertIs(type(left.panel),type(a));self.assertIs(type(right.panel),type(b))

    def test_geometry_stays_sbs_not_two_hdmi_connectors(self):
        for size in (480,720,800):
            layout=load_layout(f'product-showcase-square-sbs-{size}')
            output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                    'mode':{'width':size*2,'height':size,'refresh_hz':62.825001 if size==480 else 60}}
            self.assertEqual(geometry(output,layout),(0,0,size*2,size))
            self.assertEqual([p['shape'] for p in layout['panels']],['square','square'])
            output['mode']['width']=size
            with self.assertRaises(AppError):geometry(output,layout)
        for changes in ({'shape':'round'},{'data_source':'live'},{'view':'product-showcase'}):
            with self.assertRaises(AppError):request(**changes)
        self.assertEqual(prepare(request())[2].shapes,('square','square'))

    def test_wrappers_route_to_explicit_shape_without_changing_round_default(self):
        square=command(parser().parse_args(['start','--port','2','--shape','square','--size','720']))
        self.assertIn('product-showcase-square',square)
        self.assertIn('product-showcase-square-sbs-720',square)
        fixed=parser(default_shape='square',fixed_shape=True).parse_args(['start','--port','1'])
        self.assertIn('product-showcase-square',command(fixed))
        self.assertIn('product-showcase',command(parser().parse_args(['start','--port','1'])))
        self.assertEqual(command(parser().parse_args(['restart','--port','1'])),['restart','--port','1'])


class SquareDataTests(unittest.TestCase):
    def test_solar_home_and_grid_balance_and_cover_import_export(self):
        source=HomeDemo();directions=set()
        for t in range(0,361):
            d=source.read(t)
            self.assertAlmostEqual(d.solar_w+d.grid_w,d.house_w)
            self.assertTrue(21<=d.temperature_c<=24 and 40<=d.humidity_pct<=55)
            self.assertTrue(0<=d.light_pct<=100 and d.hvac_w>0)
            self.assertEqual(d.hvac,'COOLING' if d.temperature_c>d.target_c else 'HEATING')
            self.assertTrue(d.simulated and not d.stale)
            directions.add(d.grid_w>0)
        self.assertEqual(directions,{True,False})
        for bad in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):source.read(bad)
        self.assertEqual(source.read(50),HomeDemo().read(50))

    def test_square_pc_reuses_thermal_model_instead_of_new_fake_numbers(self):
        square,original=PcSquareDemo(),PcDemo()
        for t in (0,25,71,80,130,180):self.assertEqual(square.read(t),original.read(t))

    def test_chart_memory_is_bounded_and_prewarm_does_not_fabricate_history(self):
        h=History();h.update(1,(22,22.5))
        self.assertEqual(len(h.samples),1)
        for i in range(10000):h.update(1/30,(i%100,50))
        self.assertLessEqual(len(h.samples),51)
        p=Mock();h.draw(p,(0,0,400,100),((0,100),(0,100)))
        for call in p.line.call_args_list:
            for x,y in call.args[1:3]:
                self.assertTrue(0<=x<=400 and 0<=y<=100)


if __name__=='__main__':unittest.main()
