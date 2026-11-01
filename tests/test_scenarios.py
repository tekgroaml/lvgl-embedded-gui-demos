"""Acceptance properties for scene selection and physically linked demo motion."""
import json
import math
from pathlib import Path
import tempfile
import unittest

from gauges.scenarios import FlightDemo,ProcessDemo,make_scene
from scene_app.worker import Worker
from unittest.mock import Mock
from gauges.process_panels import ProcessTrends
from scene_app.config import normalize,prepare
from scene_app.config import load_layout
from scene_app.display import geometry
from scene_app.errors import AppError


def request(view,shape,**extra):
    return normalize({'port':1,'shape':shape,'panels':2,'input':'none','content':'different',
                      'view':view,'layout':f'{view}-sbs-480',**extra})


class SceneSelectionTests(unittest.TestCase):
    def test_dual480_native_edid_rate_is_accepted_without_accepting_other_modes(self):
        layout=load_layout('flight-sbs-480')
        output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                'mode':{'width':960,'height':480,'refresh_hz':62.825001}}
        self.assertEqual(geometry(output,layout),(0,0,960,480))
        self.assertEqual(request('flight','round')['layout_version'],'1.1.0')
        for rate in (60,59.94,62.825226):
            output['mode']['refresh_hz']=rate
            self.assertEqual(geometry(output,layout),(0,0,960,480))
        for rate in (51.85,75):
            output['mode']['refresh_hz']=rate
            with self.assertRaises(AppError):geometry(output,layout)
        output['mode']={'width':480,'height':480,'refresh_hz':62.825226}
        with self.assertRaises(AppError):geometry(output,layout)
        output['mode']={'width':960,'height':480,'refresh_hz':62.825226}
        with self.assertRaises(AppError):geometry(output,load_layout('automotive-industrial-sbs-480'))

    def test_shape_broadcast_and_exact_scene_layout_pair(self):
        for view,shape in [('flight','round'),('industrial','square')]:
            value=request(view,shape)
            self.assertEqual(value['shape'],[shape,shape])
            self.assertEqual(value['profile_id'],'sbs-'+view)
            no_view=dict(value);no_view.pop('view')
            self.assertEqual(normalize(no_view)['view'],view)
            _,_,source=prepare(value)
            self.assertTrue(source.read(0).simulated)
            self.assertIsNone(source.path)

    def test_new_worker_state_uses_the_selected_snapshot_not_legacy_telemetry(self):
        for view,shape,field in [('flight','round','altitude_ft'),('industrial','square','pressure_bar')]:
            worker=Worker(request(view,shape))
            _,source=make_scene(view)
            worker.persist=Mock();worker.mark_ready=Mock()
            worker.received(source.read(50),False)
            self.assertEqual(worker.state['health'],'ok')
            self.assertIn(field,worker.state['telemetry'])
            self.assertTrue(worker.has_data)
            self.assertTrue(worker.state['telemetry']['simulated'])
            self.assertEqual(worker.state['features']['profile_id'],'sbs-'+view)

    def test_crossed_layout_and_live_requests_are_rejected(self):
        for view,shape in [('flight','round'),('industrial','square')]:
            with self.assertRaises(AppError) as error:request(view,shape,data_source='live')
            self.assertEqual(error.exception.code,3)
            with self.assertRaises(AppError):request(view,shape,layout='automotive-industrial-sbs-480')
            with self.assertRaises(AppError):request(view,'round' if shape=='square' else 'square')

    def test_demo_speed_is_local_business_configuration_not_hdmi_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json'
            path.write_text('{"config_version":1,"fps":30,"demo_speed":2}')
            config,_,_=prepare(request('flight','round',config=str(path)))
            self.assertEqual(config['demo_speed'],2)
            for speed in (0,5,True,float('nan')):
                path.write_text(json.dumps({'config_version':1,'demo_speed':speed}))
                with self.assertRaises(AppError):prepare(request('flight','round',config=str(path)))


class FlightMotionTests(unittest.TestCase):
    def test_altitude_derivative_matches_vertical_speed(self):
        source=FlightDemo()
        for time in (10,50,90,105,140,190,230,270,300,359):
            sample=source.read(time)
            rate=(source.read(time+.001).altitude_ft-source.read(time-.001).altitude_ft)/.002*60
            self.assertAlmostEqual(rate,sample.vertical_speed_fpm,delta=.01)
            self.assertEqual(sample.simulated,True)
            self.assertLessEqual(abs(sample.vertical_speed_fpm),1100)

    def test_bank_and_heading_form_a_coordinated_turn(self):
        source=FlightDemo()
        for time in (5,25,70,150,225,320):
            sample=source.read(time)
            rate=(source.read(time+.001).heading_deg-source.read(time-.001).heading_deg)/.002
            expected=math.degrees(9.80665*math.tan(math.radians(sample.bank_deg))/(sample.airspeed_kt*.514444))
            self.assertAlmostEqual(rate,expected,delta=.001)
            self.assertLess(abs(sample.bank_deg),20)
            self.assertGreater(sample.pitch_deg,0 if sample.phase=='CLIMB' else -10)

    def test_cycle_is_continuous_and_visits_real_flight_phases(self):
        source=FlightDemo()
        self.assertEqual({source.read(t).phase for t in (50,150,230,320)},
                         {'CLIMB','CRUISE','DESCENT','LEVEL'})
        for boundary in (100,180,280,360):
            before,after=source.read(boundary-.001),source.read(boundary+.001)
            for field in ('altitude_ft','airspeed_kt','bank_deg','pitch_deg','heading_deg','vertical_speed_fpm'):
                self.assertLess(abs(getattr(before,field)-getattr(after,field)),.1,(boundary,field))
        self.assertGreater(source.read(50).vertical_speed_fpm,0)
        self.assertLess(source.read(230).vertical_speed_fpm,0)
        self.assertEqual(source.read(140).vertical_speed_fpm,0)

    def test_demo_uses_one_clock_and_is_repeatable(self):
        a,b=FlightDemo(),FlightDemo()
        self.assertEqual(a.read(42),b.read(42))
        self.assertEqual(a.read(42).altitude_ft,a.read(402).altitude_ft)
        for bad in (-1,float('inf'),float('nan')):
            with self.assertRaises(ValueError):a.read(bad)


class ProcessMotionTests(unittest.TestCase):
    def test_pump_load_pressure_flow_and_power_are_linked(self):
        source=ProcessDemo()
        idle=source.read(10);running=source.read(60);cooling=source.read(105)
        self.assertEqual(idle.phase,'STANDBY')
        self.assertAlmostEqual(idle.rpm,0);self.assertAlmostEqual(idle.flow_lmin,0)
        self.assertEqual(running.phase,'RUNNING')
        self.assertGreater(running.rpm,2400);self.assertGreater(running.pressure_bar,5)
        self.assertGreater(running.flow_lmin,40);self.assertGreater(running.power_kw,10)
        self.assertEqual(cooling.phase,'COOL DOWN')
        self.assertLess(cooling.rpm,1);self.assertLess(cooling.flow_lmin,.1)
        self.assertGreater(cooling.temperature_c,35,'heat should remain after the pump unloads')
        self.assertGreater(cooling.produced_liters,running.produced_liters)
        self.assertLess(cooling.power_kw,running.power_kw)

    def test_temperature_lags_load_instead_of_changing_instantly(self):
        source=ProcessDemo();samples=[source.read(t) for t in range(121)]
        load_peak=max(range(121),key=lambda i:samples[i].load_percent)
        temperature_peak=max(range(121),key=lambda i:samples[i].temperature_c)
        self.assertGreater(temperature_peak,load_peak+5)
        self.assertLess(abs(samples[31].temperature_c-samples[30].temperature_c),1)
        self.assertGreater(samples[95].temperature_c,samples[115].temperature_c)

    def test_totals_are_monotonic_and_cycle_stays_bounded(self):
        source=ProcessDemo();previous=-1
        phases=set()
        for time in range(0,361):
            data=source.read(time);phases.add(data.phase)
            self.assertGreaterEqual(data.produced_liters,previous);previous=data.produced_liters
            self.assertTrue(0<=data.rpm<=3000)
            self.assertTrue(1<=data.pressure_bar<=7)
            self.assertTrue(30<=data.temperature_c<=65)
            self.assertTrue(0<=data.flow_lmin<=66)
            self.assertTrue(data.simulated and not data.stale)
        self.assertEqual(phases,{'STANDBY','SOFT START','RUNNING','UNLOADING','COOL DOWN'})
        self.assertGreater(previous,100)

    def test_poll_frequency_does_not_change_physical_response(self):
        a,b=ProcessDemo(),ProcessDemo()
        for index in range(1201):first=a.read(index*.1)
        second=b.read(120)
        for field in ('rpm','pressure_bar','temperature_c','produced_liters'):
            self.assertAlmostEqual(getattr(first,field),getattr(second,field),delta=.02)

    def test_trend_sample_rate_is_independent_of_render_fps(self):
        data=ProcessDemo().read(30)
        for fps in (15,30,60):
            trend=ProcessTrends()
            for _ in range(fps*2):trend.update(1/fps,data)
            self.assertEqual(len(trend.samples),10)


if __name__=='__main__':unittest.main()
