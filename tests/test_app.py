"""Standard contract, geometry, process ownership and telemetry isolation."""
import contextlib
import io
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import Mock,patch

from scene_app import APP_ID,VERSION
from scene_app.cli import main,parser,spec_from_args,start,spawn,stop
from scene_app.config import normalize,prepare,context,load_layout,LAYOUT_IDS
from scene_app.display import geometry,matching_monitor,monitor,parse_outputs,test_conflict
from scene_app.display import probe
from scene_app.errors import AppError
from scene_app.worker import Worker
from scene_app import runtime
from gauges.common import TelemetrySource


VALUES={'speed':68,'rpm':2400,'temperature':68.5,'pressure':4.2,'voltage':13.8,'signal':.25}

def spec(**changes):
    return normalize({'port':1,'panels':2,'shape':'round,square','input':'none',
                      'content':'different','layout':'automotive-industrial-sbs-480',**changes})


class ContractTests(unittest.TestCase):
    def test_feature_expansion_and_shape_order(self):
        request=spec()
        self.assertEqual(request['shape'],['round','square'])
        self.assertEqual(request['input'],['none','none'])
        self.assertEqual(request,spec(input='none,none'))
        for changes in ({'shape':'square,round'},{'shape':'round'},{'input':'touch,none'},
                        {'panels':1,'shape':'round'},{'content':'same'},{'content':None},
                        {'view':'industrial'},{'layout':'../../other'}):
            with self.subTest(changes=changes),self.assertRaises(AppError) as error:spec(**changes)
            self.assertEqual(error.exception.code,3)

    def test_invalid_port_and_malformed_lists(self):
        for changes in ({'port':0},{'port':3},{'port':True},{'shape':'round,,square'},
                        {'input':'none,none,none'},{'data_source':'unknown'}):
            with self.subTest(changes=changes),self.assertRaises(AppError) as error:spec(**changes)
            self.assertEqual(error.exception.code,2)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['check','--port','1','--shape','round','--panels','2','--content','same']),3)

    def test_layout_version_does_not_silently_change_on_restart(self):
        with self.assertRaises(AppError) as error:spec(layout_version='0.1.0')
        self.assertEqual(error.exception.code,6)

    def test_private_context_still_revalidates_capabilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'context.json';request=spec()
            path.write_text(json.dumps(request));path.chmod(0o600)
            self.assertEqual(context(path),request)
            path.chmod(0o644)
            with self.assertRaises(AppError):context(path)
            path.chmod(0o600);request['content']='same';path.write_text(json.dumps(request))
            with self.assertRaises(AppError):context(path)
            request['app_version']='unknown';path.write_text(json.dumps(request))
            with self.assertRaises(AppError) as error:context(path)
            self.assertEqual(error.exception.code,6)
            args=parser().parse_args(['run','--context',str(path),'--port','1'])
            with self.assertRaises(AppError):spec_from_args(args)

    def test_demo_ignores_configured_live_file_and_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'demo.json';path.write_text(json.dumps({'config_version':1,'input_file':'missing.json'}))
            with patch.dict(os.environ,{'INPUT_FILE':'missing','SDL_VIDEODRIVER':'invalid'}):
                _,_,source=prepare(spec(config=str(path)))
            data=source.read(0)
            self.assertTrue(data.simulated);self.assertFalse(data.stale)
            self.assertIsNone(source.path)

    def test_live_requires_config_and_resolves_paths_beside_config(self):
        with self.assertRaises(AppError) as error:prepare(spec(data_source='live'))
        self.assertEqual(error.exception.code,8)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'live.json';path.write_text(json.dumps({'config_version':1,'input_file':'data.json'}))
            _,_,source=prepare(spec(data_source='live',config=str(path)))
            self.assertEqual(source.path,(root/'data.json').resolve())
            self.assertTrue(source.read(0).stale)
            (root/'data.json').write_text(json.dumps(VALUES))
            sample=source.read(1)
            self.assertFalse(sample.stale);self.assertFalse(sample.simulated);self.assertEqual(sample.speed,68)

    def test_config_schema_bounds_and_render_fps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json'
            for value in ({'config_version':2},{'config_version':1,'fps':61},
                          {'config_version':1,'fps':True},{'config_version':1,'unknown':1}):
                path.write_text(json.dumps(value))
                with self.assertRaises(AppError) as error:prepare(spec(config=str(path)))
                self.assertEqual(error.exception.code,6)

    def test_fifo_config_and_input_are_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pipe';os.mkfifo(path)
            with self.assertRaises(AppError):prepare(spec(config=str(path)))
            sample=TelemetrySource(path).read(0)
            self.assertTrue(sample.stale);self.assertFalse(sample.simulated)


class LayoutTests(unittest.TestCase):
    def test_old_unmanaged_service_is_detected_before_gui_startup(self):
        with patch('scene_app.display.subprocess.run',return_value=Mock(returncode=0)),\
             patch('scene_app.display.libraries') as gui:
            with self.assertRaises(AppError) as error:probe(1,LAYOUT_IDS[0])
            self.assertEqual(error.exception.code,4)
            gui.assert_not_called()

    def test_layouts_are_non_overlapping_full_canvas_and_explicitly_unverified_hardware(self):
        for lid in LAYOUT_IDS:
            layout=load_layout(lid);size=layout['signal_mode']['height']
            self.assertFalse(layout['verification']['hardware_verified'])
            self.assertIsNone(layout['product_match'])
            a,b=layout['panels']
            self.assertEqual(a['rect'],{'x':0,'y':0,'width':size,'height':size})
            self.assertEqual(b['rect'],{'x':size,'y':0,'width':size,'height':size})
            self.assertEqual(layout['signal_mode']['width'],size*2)

    def test_damaged_layout_is_not_accepted(self):
        original=load_layout(LAYOUT_IDS[0]);original['panels'][1]['rect']['x']=0
        with patch('scene_app.config.read_json',return_value=(original,'digest')):
            with self.assertRaises(AppError) as error:load_layout(LAYOUT_IDS[0])
            self.assertEqual(error.exception.code,6)

    def test_wrong_mode_rate_scale_or_rotation_rejected(self):
        output={'enabled':True,'position':[800,0],'scale':1,'transform':'normal',
                'mode':{'width':960,'height':480,'refresh_hz':60}}
        layout=load_layout(LAYOUT_IDS[0])
        self.assertEqual(geometry(output,layout),(800,0,960,480))
        for changes in ({'enabled':False},{'scale':2},{'transform':'90'},
                        {'mode':{'width':800,'height':800,'refresh_hz':60}},
                        {'mode':{'width':960,'height':480,'refresh_hz':51.85}}):
            with self.subTest(changes=changes),self.assertRaises(AppError):geometry({**output,**changes},layout)

    def test_connector_mapping_does_not_depend_on_enumeration(self):
        text='''HDMI-A-1 "SBS"
  Enabled: yes
  Modes:
    960x480 px, 60.000000 Hz (current)
  Position: 800,0
  Transform: normal
  Scale: 1.000000
'''
        outputs=parse_outputs(text);expected=geometry(outputs['HDMI-A-1'],load_layout(LAYOUT_IDS[0]))
        self.assertEqual(matching_monitor([(0,0,800,800),expected],expected),1)
        with self.assertRaises(AppError):matching_monitor([expected,expected],expected)
        outputs['HDMI-A-2']={**outputs['HDMI-A-1'],'scale':2,
                              'mode':{'width':1920,'height':960,'refresh_hz':60}}
        with patch('scene_app.display.outputs',return_value=outputs):
            with self.assertRaises(AppError):monitor(1,Mock(),load_layout(LAYOUT_IDS[0]))


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ,{'XDG_RUNTIME_DIR':self.tmp.name,'XDG_STATE_HOME':self.tmp.name})
        self.env.start()
    def tearDown(self):self.env.stop();self.tmp.cleanup()

    def test_shared_connector_lock_and_foreign_owner_is_not_signalled(self):
        fd=runtime.lease(1)
        try:
            with self.assertRaises(AppError) as error:runtime.lease(1)
            self.assertEqual(error.exception.code,4)
            runtime.atomic_json(runtime.paths(1)['state'],{'app_id':'single-round-homeassistant-kiosk','status':'running'})
            self.assertEqual(runtime.status(1)['status'],'occupied')
            with patch('scene_app.cli.runtime.rpc',side_effect=AppError('Foreign owner',4)),patch('os.kill') as kill:
                with self.assertRaises(AppError):stop(1)
                kill.assert_not_called()
        finally:os.close(fd)

    def test_stale_instance_is_not_a_reason_to_signal_a_pid(self):
        runtime.base(True)
        runtime.atomic_json(runtime.paths(1)['state'],{'app_id':APP_ID,'port':1,'pid':os.getpid(),'status':'running'})
        with patch('os.kill',side_effect=AssertionError('Do not signal PID files')):
            self.assertEqual(runtime.status(1)['status'],'stopped')

    def test_stale_screen_test_socket_not_a_conflict(self):
        path=Path(self.tmp.name)/'pi-setting-test/control.sock';path.parent.mkdir()
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:connection.bind(str(path))
        test_conflict(1)
        self.assertTrue(path.exists())

    def test_control_protocol_rejects_wrong_app_or_instance(self):
        runtime.base(True);worker=Worker(spec(),'fixture-instance');worker.GLib=Mock()
        worker.control=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        worker.control.bind(str(runtime.paths(1)['socket']));worker.control.listen(4);worker.control.settimeout(.1)
        thread=threading.Thread(target=worker.controls,daemon=True);thread.start()
        try:
            self.assertEqual(runtime.rpc(1)['instance_id'],'fixture-instance')
            with self.assertRaises(AppError):runtime.rpc(1,'stop','other-instance')
            worker.GLib.idle_add.assert_not_called()
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
                client.connect(str(runtime.paths(1)['socket']));client.sendall(b'{"action":"stop","app_id":"other-project"}\n')
                self.assertFalse(runtime.receive(client)['ok'])
            runtime.rpc(1,'stop','fixture-instance');worker.GLib.idle_add.assert_called_once()
        finally:worker.quitting=True;worker.control.close();thread.join(timeout=1)


class LifecycleTests(unittest.TestCase):
    def test_idempotent_start_does_not_spawn_second_scene(self):
        request=spec()
        with patch('scene_app.cli.preflight',return_value=({},'digest')),patch('scene_app.cli.runtime.locked',return_value=True),\
             patch('scene_app.cli.runtime.rpc',return_value={'version':VERSION,'features':request,'config_digest':'digest','status':'running'}),\
             patch('scene_app.cli.spawn') as spawn:
            self.assertEqual(start(request,{})['status'],'running');spawn.assert_not_called()

    def test_failed_same_app_replacement_restores_previous_layout_and_config(self):
        old,new=spec(),spec(layout='automotive-industrial-sbs-720')
        with patch('scene_app.cli.preflight',return_value=({},'digest')),patch('scene_app.cli.runtime.locked',return_value=True),\
             patch('scene_app.cli.runtime.rpc',return_value={'version':VERSION,'features':old,'config_digest':'old','status':'running'}),\
             patch('scene_app.cli.stop'),patch('scene_app.cli.spawn',side_effect=[AppError('failed'),{'status':'running'}]) as spawn:
            with self.assertRaises(AppError) as error:start(new,{},replace=True)
            self.assertIn('restored',str(error.exception));self.assertEqual(spawn.call_args_list[-1].args[0],old)

    def test_other_version_cannot_be_replaced_with_false_rollback_promise(self):
        with patch('scene_app.cli.preflight',return_value=({},'digest')),patch('scene_app.cli.runtime.locked',return_value=True),\
             patch('scene_app.cli.runtime.rpc',return_value={'version':'unknown'}),patch('scene_app.cli.stop') as stop:
            with self.assertRaises(AppError) as error:start(spec(),{},replace=True)
            self.assertEqual(error.exception.code,6);stop.assert_not_called()

    def test_native_crash_has_standard_error_and_request_file_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'XDG_RUNTIME_DIR':tmp,'XDG_STATE_HOME':tmp}),\
             patch('scene_app.cli.runtime.read_state',return_value={}),patch('scene_app.cli.subprocess.Popen') as popen:
            popen.return_value.poll.return_value=-11
            with self.assertRaises(AppError) as error:spawn(spec(),{})
            self.assertEqual(error.exception.code,7)
            self.assertFalse(list(runtime.base().glob('.start-*.json')))

    def test_stale_live_data_remains_live_and_degraded(self):
        worker=Worker(spec(data_source='live'))
        worker.persist=Mock();worker.mark_ready=Mock()
        worker.received(TelemetrySource(Path('/nonexistent/input')).read(0),False)
        self.assertEqual(worker.state['health'],'degraded-stale-telemetry')
        self.assertFalse(worker.state['telemetry']['simulated'])
        self.assertFalse(worker.has_data)


if __name__=='__main__':unittest.main()
