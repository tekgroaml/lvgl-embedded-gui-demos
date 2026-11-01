"""PC-case scene links, honest missing sensors and remote-origin freshness."""
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock,patch

from scenes.pc_monitor.model import PcDemo,PcJsonSource,decode_snapshot,targets
from scenes.pc_monitor.panels import value
from scene_app.config import normalize,prepare,load_layout
from scene_app.display import geometry
from scene_app.worker import Worker
from scene_app.errors import AppError


def request(**changes):
    return normalize({'port':1,'shape':'round','panels':2,'input':'none','content':'different',
                      'view':'pc-monitor','layout':'pc-monitor-sbs-480',**changes})


def snapshot(**changes):
    return {'schema_version':1,'sampled_at':time.time(),'pc_name':'DESKTOP-PC','cpu_load_pct':35,
            'memory_used_gb':12,'memory_total_gb':32,**changes}


class PcDemoTests(unittest.TestCase):
    def test_duty_cycle_includes_idle_cpu_gpu_and_cooling(self):
        source=PcDemo()
        idle=source.read(10);cpu=source.read(50);gpu=source.read(100);cool=source.read(175)
        self.assertEqual([d.workload for d in (idle,cpu,gpu,cool)],['IDLE','CPU RENDER','GAMING','COOLING'])
        self.assertGreater(cpu.cpu_load_pct,gpu.cpu_load_pct)
        self.assertGreater(gpu.gpu_load_pct,cpu.gpu_load_pct)
        self.assertGreater(cpu.cpu_power_w,idle.cpu_power_w)
        self.assertGreater(gpu.gpu_power_w,cpu.gpu_power_w)
        self.assertGreater(gpu.gpu_temp_c,cpu.gpu_temp_c)
        self.assertGreater(gpu.gpu_fan_rpm,cpu.gpu_fan_rpm)
        self.assertLess(cool.gpu_temp_c,gpu.gpu_temp_c)
        self.assertTrue(all(d.simulated and not d.stale for d in (idle,cpu,gpu,cool)))

    def test_thermal_response_and_fans_lag_gpu_load(self):
        source=PcDemo();samples=[source.read(t) for t in range(181)]
        self.assertGreater(samples[125].gpu_temp_c,samples[75].gpu_temp_c)
        self.assertGreater(samples[130].gpu_fan_rpm,samples[75].gpu_fan_rpm)
        self.assertGreater(samples[145].gpu_temp_c,samples[10].gpu_temp_c)
        for before,after in zip(samples,samples[1:]):
            self.assertLess(abs(after.cpu_temp_c-before.cpu_temp_c),4)
            self.assertLess(abs(after.gpu_temp_c-before.gpu_temp_c),4)
            self.assertLess(abs(after.cpu_fan_rpm-before.cpu_fan_rpm),150)
        for t in range(0,360):
            sample=source.read(t+181)
            self.assertTrue(0<=sample.cpu_load_pct<=100 and 0<=sample.gpu_load_pct<=100)
            self.assertTrue(0<=sample.memory_used_gb<=sample.memory_total_gb)
            self.assertTrue(0<=sample.vram_used_gb<=sample.vram_total_gb)
            self.assertTrue(0<=sample.cpu_fan_rpm<=4000 and 0<=sample.gpu_fan_rpm<=4000)

    def test_shared_clock_and_sampling_do_not_change_model(self):
        a,b=PcDemo(),PcDemo()
        for i in range(1801):first=a.read(i*.1)
        second=b.read(180)
        for name in ('cpu_temp_c','gpu_temp_c','cpu_fan_rpm','gpu_fan_rpm'):
            self.assertAlmostEqual(getattr(first,name),getattr(second,name),delta=.1)
        for boundary in (15,30,60,75,120,140,180):
            before,after=targets(boundary-.0001),targets(boundary+.0001)
            self.assertLess(abs(before[0]-after[0]),.01)
            self.assertLess(abs(before[1]-after[1]),.01)
        for invalid in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):a.read(invalid)


class PcSnapshotTests(unittest.TestCase):
    def test_missing_sensors_stay_unavailable_not_zero_or_simulated(self):
        data=decode_snapshot(snapshot(),time.time())
        self.assertFalse(data.simulated);self.assertFalse(data.stale)
        for name in ('cpu_temp_c','gpu_temp_c','gpu_load_pct','cpu_fan_rpm','gpu_fan_rpm','cpu_power_w'):
            self.assertIsNone(getattr(data,name))
        self.assertEqual(value(None),'—')
        self.assertEqual(value(0),'0')
        self.assertEqual(decode_snapshot(snapshot(gpu_fan_rpm=0),time.time()).gpu_fan_rpm,0)

    def test_invalid_metrics_cannot_be_labelled_live(self):
        for changes in ({'cpu_load_pct':True},{'gpu_temp_c':float('nan')},{'cpu_load_pct':101},
                        {'memory_used_gb':33},{'vram_used_gb':3},{'pc_name':'a\nb'},
                        {'schema_version':2},{'sampled_at':float('inf')},{'cpu_fan_rpm':-5},
                        {'vram_used_gb':14,'vram_total_gb':12}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):decode_snapshot(snapshot(**changes),time.time())

    def test_payload_timestamp_not_upload_mtime_decides_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pc.json'
            path.write_text(json.dumps(snapshot(sampled_at=time.time()-20)))
            os.utime(path,None)
            source=PcJsonSource(path);data=source.read(0)
            self.assertTrue(data.stale);self.assertFalse(data.simulated)
            self.assertIsNone(data.cpu_load_pct)
            path.write_text(json.dumps(snapshot(cpu_temp_c=65)))
            fresh=source.read(1);self.assertFalse(fresh.stale);self.assertEqual(fresh.cpu_temp_c,65)
            path.write_text(json.dumps(snapshot(sampled_at=time.time()-20,cpu_temp_c=20)))
            data=source.read(2)
            self.assertTrue(data.stale);self.assertEqual(data.cpu_temp_c,65,'keep last good values, never replace with old data')
            path.write_text('{"bad":true}')
            self.assertFalse(source.read(3).simulated)
            self.assertTrue(source.read(3).stale)

    def test_clock_skew_future_data_is_not_accepted(self):
        now=time.time()
        self.assertTrue(decode_snapshot(snapshot(sampled_at=now+10),now).stale)
        self.assertTrue(decode_snapshot(snapshot(sampled_at=now-6),now).stale)
        self.assertFalse(decode_snapshot(snapshot(sampled_at=now),now).stale)

    def test_delayed_but_fresh_upload_cannot_roll_back_newer_pc_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pc.json';now=time.time()
            path.write_text(json.dumps(snapshot(sampled_at=now,cpu_load_pct=80)))
            source=PcJsonSource(path)
            self.assertEqual(source.read(0).cpu_load_pct,80)
            path.write_text(json.dumps(snapshot(sampled_at=now-1,cpu_load_pct=10)))
            retained=source.read(1)
            self.assertEqual(retained.cpu_load_pct,80)
            self.assertFalse(retained.stale)

    def test_missing_or_special_files_do_not_block_or_synthesize_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pipe';os.mkfifo(path)
            for filename in (path,Path(tmp)/'missing'):
                sample=PcJsonSource(filename).read(0)
                self.assertTrue(sample.stale);self.assertFalse(sample.simulated)
        with self.assertRaises(ValueError):PcJsonSource(None)


class PcContractTests(unittest.TestCase):
    def test_scene_layout_source_and_native_dual480_rate(self):
        spec=request();self.assertEqual(spec['profile_id'],'sbs-pc-monitor')
        no_view=dict(spec);no_view.pop('view')
        self.assertEqual(normalize(no_view)['view'],'pc-monitor')
        output={'enabled':True,'position':[0,0],'scale':1,'transform':'normal',
                'mode':{'width':960,'height':480,'refresh_hz':62.825001}}
        self.assertEqual(geometry(output,load_layout('pc-monitor-sbs-480')),(0,0,960,480))
        for changes in ({'shape':'square'},{'view':'flight'},{'input':'touch'},{'content':'same'}):
            with self.assertRaises(AppError):request(**changes)

    def test_demo_never_queries_local_pc_or_pi_stats(self):
        with patch('subprocess.run',side_effect=AssertionError('no host sensor collection')):
            _,_,source=prepare(request())
            self.assertTrue(source.read(30).simulated)
        with self.assertRaises(AppError) as error:prepare(request(data_source='live'))
        self.assertEqual(error.exception.code,8)

    def test_live_is_remote_pc_schema_and_worker_reports_unavailable_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);path=directory/'pc.json';path.write_text(json.dumps(snapshot()))
            config=directory/'config.json';config.write_text('{"config_version":1,"input_file":"./pc.json"}')
            spec=request(data_source='live',config=str(config))
            _,_,source=prepare(spec)
            self.assertEqual(source.path,path.resolve())
            worker=Worker(spec);self.assertIsNone(worker.data)
            worker.persist=Mock();worker.mark_ready=Mock()
            worker.received(source.read(0),False)
            self.assertTrue(worker.has_data)
            self.assertFalse(worker.state['telemetry']['simulated'])
            self.assertEqual(worker.state['telemetry']['pc_name'],'DESKTOP-PC')
            self.assertIsNone(worker.state['telemetry']['gpu_temp_c'])
            self.assertIsNone(worker.state['telemetry']['cpu_fan_rpm'])


if __name__=='__main__':unittest.main()
