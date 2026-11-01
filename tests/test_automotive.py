"""Dual-round automotive behavior and registry-based scene isolation."""
from dataclasses import asdict
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from common.telemetry import Telemetry,JsonTelemetrySource
from scenes.registry import DEFINITIONS,LAYOUTS,SCENES,make_scene
from scenes.automotive.model import AutomotiveDemo,driving_profile,drivetrain
from scene_app.config import normalize,prepare,load_layout
from scene_app.display import geometry
from scene_app.worker import Worker
from scene_app.errors import AppError


def request(**changes):
    return normalize({'port':1,'shape':'round','panels':2,'input':'none','content':'different',
                      'view':'automotive','layout':'automotive-sbs-480',**changes})


class AutomotiveContractTests(unittest.TestCase):
    def test_new_profile_is_selected_by_view_or_explicit_layout_without_breaking_flight(self):
        value=request()
        self.assertEqual(value['profile_id'],'sbs-automotive')
        self.assertEqual(value['shape'],['round','round'])
        inferred=dict(value);inferred.pop('view')
        self.assertEqual(normalize(inferred)['view'],'automotive')
        inferred['layout']='flight-sbs-480';inferred.pop('layout_version')
        self.assertEqual(normalize(inferred)['view'],'flight')
        for changes in ({'shape':'square'},{'view':'flight'},{'input':'touch'},
                        {'content':'same'},{'data_source':'live'}):
            with self.subTest(changes=changes),self.assertRaises(AppError) as error:request(**changes)
            self.assertEqual(error.exception.code,3)

    def test_native_dual480_rate_is_scene_specific_and_does_not_change_geometry(self):
        output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                'mode':{'width':960,'height':480,'refresh_hz':62.825001}}
        self.assertEqual(geometry(output,load_layout('automotive-sbs-480')),(0,0,960,480))
        self.assertEqual(geometry(output,load_layout('flight-sbs-480')),(0,0,960,480))
        for lid in ('industrial-sbs-480','automotive-industrial-sbs-480'):
            with self.assertRaises(AppError):geometry(output,load_layout(lid))
        output['mode']['refresh_hz']=75
        with self.assertRaises(AppError):geometry(output,load_layout('automotive-sbs-480'))

    def test_demo_ignores_an_input_file_and_worker_reports_the_automotive_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json'
            path.write_text('{"config_version":1,"input_file":"missing.json"}')
            _,_,source=prepare(request(config=str(path)))
            self.assertIsInstance(source,AutomotiveDemo)
            self.assertTrue(source.read(50).simulated)
        worker=Worker(request());worker.persist=Mock();worker.mark_ready=Mock()
        worker.received(AutomotiveDemo().read(50),False)
        self.assertIn('fuel_percent',worker.state['telemetry'])
        self.assertIn('speed_kmh',worker.state['telemetry'])
        self.assertTrue(worker.has_data)
        self.assertEqual(worker.state['health'],'ok')


class AutomotiveModelTests(unittest.TestCase):
    def test_driving_cycle_visits_idle_acceleration_cruise_and_braking(self):
        demo=AutomotiveDemo()
        idle=demo.read(5);accel=demo.read(35);cruise=demo.read(75);braking=demo.read(125);parked=demo.read(160)
        self.assertEqual([x.phase for x in (idle,accel,cruise,braking,parked)],
                         ['IDLE','ACCELERATING','CRUISING','BRAKING','IDLE'])
        self.assertEqual(idle.speed_kmh,0);self.assertAlmostEqual(idle.rpm,850)
        self.assertGreater(accel.speed_kmh,20);self.assertGreater(accel.load_percent,cruise.load_percent)
        self.assertGreater(cruise.speed_kmh,100)
        self.assertLess(braking.load_percent,cruise.load_percent)
        self.assertEqual(parked.speed_kmh,0);self.assertEqual(parked.gear,0)
        self.assertGreater(parked.coolant_c,idle.coolant_c)

    def test_speed_derivative_and_cycle_joins_are_continuous(self):
        for time in (5,20,35,60,78,110,130,170):
            speed,accel,_=driving_profile(time)
            derivative=(driving_profile(time+.001)[0]-driving_profile(time-.001)[0])/.002
            self.assertAlmostEqual(derivative,accel,delta=.001)
        for boundary in (12,52,102,142,180):
            before,after=driving_profile(boundary-.001),driving_profile(boundary+.001)
            self.assertLess(abs(before[0]-after[0]),.01)
            self.assertLess(abs(before[1]-after[1]),.01)

    def test_upshift_drops_rpm_without_reversing_the_speed(self):
        for speed in (22,42,62,85):
            low=drivetrain(speed-.01,2)
            high=drivetrain(speed+.01,2)
            self.assertEqual(high[0],low[0]+1)
            self.assertLess(high[1],low[1])
        for speed in range(181):
            gear,rpm,load=drivetrain(speed,1)
            self.assertTrue(0<=gear<=5)
            self.assertTrue(800<=rpm<7000)
            self.assertTrue(0<=load<=100)

    def test_temperature_lags_load_fuel_and_distance_are_integrated(self):
        demo=AutomotiveDemo();values=[demo.read(t) for t in range(361)]
        peak_load=max(range(143),key=lambda i:values[i].load_percent)
        peak_temperature=max(range(143),key=lambda i:values[i].coolant_c)
        self.assertGreater(peak_temperature,peak_load+10)
        for a,b in zip(values,values[1:]):
            self.assertGreaterEqual(b.trip_km,a.trip_km)
            self.assertLessEqual(b.fuel_percent,a.fuel_percent)
            self.assertLess(abs(b.coolant_c-a.coolant_c),1)
            self.assertTrue(0<=b.fuel_percent<=100)
            self.assertTrue(12<=b.voltage_v<=15)
            self.assertTrue(.5<=b.oil_pressure_bar<=5)
            self.assertTrue(b.simulated and not b.stale)
        self.assertGreater(values[-1].trip_km,3)
        self.assertLess(values[-1].fuel_percent,values[0].fuel_percent)
        # No tank or trip reset when the speed cycle wraps.
        self.assertEqual(values[181].trip_km,values[179].trip_km)  # stationary at the boundary
        self.assertGreater(values[220].trip_km,values[179].trip_km)
        self.assertLess(values[181].fuel_percent,values[179].fuel_percent)

    def test_snapshot_frequency_and_reset_are_deterministic(self):
        a,b=AutomotiveDemo(),AutomotiveDemo()
        for index in range(1801):x=a.read(index*.1)
        y=b.read(180)
        for field in ('coolant_c','fuel_percent','trip_km'):
            self.assertAlmostEqual(getattr(x,field),getattr(y,field),delta=.002)
        a.read(0)
        self.assertEqual(a.read(40),AutomotiveDemo().read(40))
        for bad in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):a.read(bad)


class SceneArchitectureTests(unittest.TestCase):
    def test_every_registry_entry_owns_panels_model_and_versioned_layouts(self):
        for name,scene in DEFINITIONS.items():
            with self.subTest(scene=name):
                panels,source=make_scene(name)
                self.assertEqual(len(panels),2)
                self.assertTrue(all(type(panel).__module__.startswith(scene.owner_package) for panel in panels))
                self.assertTrue(type(source).__module__.startswith(scene.owner_package))
                for size in scene.sizes:
                    self.assertTrue(Path(scene.layout_path(size)).is_file())
                    layout=load_layout(f'{scene.prefix}-{size}')
                    self.assertEqual([p['view'] for p in layout['panels']],list(scene.panel_ids))
                    self.assertEqual(layout['version'],scene.layout_version(size))

    def test_legacy_modules_are_aliases_of_the_same_implementations(self):
        from gauges.scenarios import FlightDemo,ProcessDemo
        from scenes.flight.model import FlightDemo as NewFlight
        from scenes.industrial.model import ProcessDemo as NewProcess
        from gauges.automotive_gauge import AutomotiveGauge
        from scenes.automotive_industrial.automotive_panel import AutomotiveGauge as NewAutomotive
        from gauges.industrial_panel import IndustrialPanel
        from scenes.automotive_industrial.industrial_panel import IndustrialPanel as NewIndustrial
        self.assertIs(FlightDemo,NewFlight);self.assertIs(ProcessDemo,NewProcess)
        self.assertIs(AutomotiveGauge,NewAutomotive);self.assertIs(IndustrialPanel,NewIndustrial)

    def test_shared_live_reader_cannot_fall_back_to_demo_and_standard_worker_has_no_fake_initial_data(self):
        with self.assertRaises(ValueError):JsonTelemetrySource(None)
        mixed=normalize({'port':1,'panels':2,'shape':'round,square','input':'none','content':'different',
                         'view':'automotive-industrial','layout':'automotive-industrial-sbs-480','data_source':'live'})
        worker=Worker(mixed)
        self.assertIsNone(worker.data)
        worker.persist=Mock();worker.received(None,True)
        self.assertFalse(worker.has_data)
        self.assertEqual(worker.state['health'],'degraded-stale-telemetry')

    def test_new_capabilities_manifest_matches_registry(self):
        from scripts.update_manifest import update
        data=json.loads(Path('screen-app.json').read_text())
        self.assertEqual(update(json.loads(json.dumps(data))),data)


if __name__=='__main__':unittest.main()
