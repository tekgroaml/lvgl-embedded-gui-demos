"""Native GTK layer-shell worker for a single-output, two-panel SBS scene."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
import os
import signal
import socket
import sys
import threading
import time
import uuid

from . import APP_ID, VERSION, display, runtime
from .config import normalize, prepare, load_layout
from .errors import AppError
from .painter import draw_scene
from gauges.common import Telemetry
from gauges.automotive_gauge import AutomotiveGauge
from gauges.industrial_panel import IndustrialPanel


class Worker:
    def __init__(self, spec, instance_id=None):
        self.spec=normalize(spec)
        self.instance_id=instance_id or uuid.uuid4().hex
        self.port=self.spec['port']
        self.layout=load_layout(self.spec['layout'])
        self.exit_code=0
        self.quitting=self.ready=self.drawn=self.polling=self.has_data=False
        self.control=self.window=self.executor=self.lease=None
        self.data=Telemetry(stale=self.spec['data_source']=='live',simulated=self.spec['data_source']=='demo')
        self.automotive,self.industrial=AutomotiveGauge(),IndustrialPanel()
        self.state={'app_id':APP_ID,'version':VERSION,'contract_version':1,'instance_id':self.instance_id,
                    'owner':os.getuid(),'port':self.port,'connector':f'HDMI-A-{self.port}',
                    'status':'starting','health':'starting','renderer':'python-gtk-cairo',
                    'features':self.spec,'layout':{'id':self.layout['id'],'version':self.layout['version']},
                    'panels':self.layout['panels'],'hardware_verified':False,'frames':0}

    def persist(self):
        runtime.atomic_json(runtime.paths(self.port)['state'],self.state)

    def event(self,name,**details):
        print(json.dumps({'contract_version':1,'instance_id':self.instance_id,'event':name,'details':details}),flush=True)

    def quit(self,*_):
        if self.quitting:return False
        self.quitting=True
        if self.window:self.window.destroy()
        self.Gtk.main_quit()
        return False

    def fail(self,message,code=7):
        if self.quitting:return False
        self.exit_code=code
        self.state.update(status='failed',health='failed',error=message,error_code=code)
        self.persist();self.event('error',message=message,code=code);self.quit()
        return False

    def controls(self):
        while not self.quitting:
            try:client,_=self.control.accept()
            except (OSError,socket.timeout):continue
            with client:
                client.settimeout(2)
                try:
                    message=runtime.receive(client)
                    if message.get('app_id')!=APP_ID or message.get('instance_id',self.instance_id)!=self.instance_id:
                        reply={'ok':False,'code':4,'error':'Instance ownership mismatch.'}
                    elif message.get('action') not in ('status','stop'):
                        reply={'ok':False,'code':2,'error':'Unknown action.'}
                    else:
                        reply={'ok':True,'state':dict(self.state)}
                        if message['action']=='stop':self.GLib.idle_add(self.quit)
                    client.sendall(json.dumps(reply).encode()+b'\n')
                except (OSError,ValueError):pass

    def verify_surface(self):
        selected=self.Gdk.Display.get_default().get_monitor_at_window(self.window.get_window())
        geometry=self.target.get_geometry();allocation=self.area.get_allocation()
        if (selected!=self.target or (geometry.x,geometry.y,geometry.width,geometry.height)!=self.expected
                or (allocation.width,allocation.height)!=self.expected[2:]):
            self.fail('The actual SBS surface does not match the selected HDMI output/layout.',3)
            return False
        return True

    def mark_ready(self):
        if self.quitting or self.ready or not self.drawn or not self.has_data:return False
        if self.verify_surface():
            self.ready=True
            self.state.update(status='running',health='ok',started_at=time.time())
            self.persist()
            self.event('ready',connector=self.state['connector'],viewport=self.state['viewport'],layout=self.state['layout'])
        return False

    def paint(self,area,context):
        if self.quitting:return False
        try:
            draw_scene(context,self.layout,self.automotive,self.industrial,self.data)
            self.drawn=True
            self.state['frames']+=1
            if not self.ready:self.GLib.idle_add(self.mark_ready)
        except Exception as exc:
            self.GLib.idle_add(self.fail,f'Native SBS drawing failed ({type(exc).__name__}).',7)
        return False

    def animate(self):
        if self.quitting:return False
        now=time.monotonic();dt=min(now-self.previous,.1);self.previous=now
        self.automotive.update(dt,self.data);self.industrial.update(dt,self.data)
        self.area.queue_draw()
        return True

    def poll(self):
        if self.quitting:return False
        if self.polling:return True
        self.polling=True
        def completed(future):
            try:value,error=future.result(),False
            except Exception:value,error=None,True
            if not self.quitting:self.GLib.idle_add(self.received,value,error)
        self.executor.submit(self.source.read,time.monotonic()-self.begin).add_done_callback(completed)
        return True

    def received(self,value,error):
        self.polling=False
        if self.quitting:return False
        if error:
            self.data.stale=True
        else:
            self.data=value
        if not self.data.stale:self.has_data=True
        self.state['health']='degraded-stale-telemetry' if self.data.stale else 'ok'
        self.state['telemetry']=asdict(self.data)
        self.persist();self.mark_ready()
        return False

    def tick(self):
        if self.quitting:return False
        if not self.ready and time.monotonic()-self.begin>28:
            return self.fail('SBS scene did not become ready. Live mode requires a fresh valid JSON snapshot.')
        try:
            display.test_conflict(self.port)
            output,_,expected=display.monitor(self.port,self.Gdk,self.layout)
            if expected!=self.expected or output['mode']!=self.state['native_mode']:
                return self.fail('Display mode/position changed. Configure it and restart the scene.',3)
            if self.ready and not self.verify_surface():return False
        except AppError as exc:return self.fail(str(exc),exc.code)
        if self.ready:
            self.persist();self.event('health',health=self.state['health'],frames=self.state['frames'])
        return True

    def run(self):
        self.lease=runtime.lease(self.port)
        try:
            self.config,digest,self.source=prepare(self.spec)
            self.state['config_digest']=digest
            self.Gdk,self.GLib,self.Gtk,layer=display.libraries()
            ok=self.Gtk.init_check()
            if not (ok[0] if isinstance(ok,tuple) else ok) or not layer.is_supported():
                raise AppError('Use the logged-in Wayland layer-shell desktop.',5)
            display.test_conflict(self.port)
            output,self.target,self.expected=display.monitor(self.port,self.Gdk,self.layout)
            self.state.update(native_mode=output['mode'],viewport={'width':self.expected[2],'height':self.expected[3]},
                              output_binding='gtk-layer-shell',profile_id='sbs-automotive-industrial')
            self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='instrument-data')
            self.control=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            path=runtime.paths(self.port)['socket'];path.unlink(missing_ok=True)
            self.control.bind(str(path));path.chmod(0o600);self.control.listen(8);self.control.settimeout(.5)
            threading.Thread(target=self.controls,daemon=True).start()
            self.persist()
            self.window=self.Gtk.Window(title='Instruments · '+self.state['connector'])
            self.window.set_decorated(False)
            layer.init_for_window(self.window);layer.set_namespace(self.window,APP_ID+f'-port{self.port}')
            layer.set_layer(self.window,layer.Layer.OVERLAY);layer.set_monitor(self.window,self.target)
            layer.set_exclusive_zone(self.window,-1)
            layer.set_keyboard_mode(self.window,getattr(layer.KeyboardMode,'ON_DEMAND',layer.KeyboardMode.NONE))
            for edge in (layer.Edge.TOP,layer.Edge.BOTTOM,layer.Edge.LEFT,layer.Edge.RIGHT):
                layer.set_anchor(self.window,edge,True);layer.set_margin(self.window,edge,0)
            self.area=self.Gtk.DrawingArea();self.area.connect('draw',self.paint);self.window.add(self.area)
            self.window.connect('delete-event',lambda *_:(self.quit(),True)[1])
            self.window.connect('key-press-event',self.key);self.window.connect('realize',self.hide_cursor)
            self.begin=self.previous=time.monotonic()
            self.GLib.unix_signal_add(self.GLib.PRIORITY_DEFAULT,signal.SIGTERM,self.quit)
            self.GLib.unix_signal_add(self.GLib.PRIORITY_DEFAULT,signal.SIGINT,self.quit)
            self.window.show_all();self.poll()
            self.GLib.timeout_add(max(1,round(1000/self.config['fps'])),self.animate)
            self.GLib.timeout_add(200,self.poll);self.GLib.timeout_add_seconds(10,self.tick)
            self.Gtk.main()
        except AppError as exc:
            self.state.update(status='failed',health='failed',error=str(exc),error_code=exc.code)
            self.exit_code=exc.code;self.event('error',message=str(exc),code=exc.code)
        except Exception as exc:
            self.state.update(status='failed',health='failed',error=f'Native SBS scene failed ({type(exc).__name__}).',error_code=7)
            self.exit_code=7;self.event('error',message=self.state['error'],code=7)
        finally:
            self.quitting=True
            if self.window:self.window.destroy()
            if self.executor:self.executor.shutdown(wait=True,cancel_futures=True)
            if self.control:
                self.control.close();runtime.paths(self.port)['socket'].unlink(missing_ok=True)
            if self.state['status']!='failed':self.state.update(status='stopped',health='stopped')
            self.persist();self.event('stopped',status=self.state['status']);os.close(self.lease)
        return self.exit_code

    def key(self,_,event):
        if event.keyval in (self.Gdk.KEY_Escape,self.Gdk.KEY_q):
            self.quit();return True
        return False

    def hide_cursor(self,*_):
        self.window.get_window().set_cursor(self.Gdk.Cursor.new_for_display(self.Gdk.Display.get_default(),self.Gdk.CursorType.BLANK_CURSOR))


def main():
    from .config import read_json
    request,_=read_json(sys.argv[1])
    try:return Worker(request['spec'],request['instance_id']).run()
    except AppError as exc:
        print(json.dumps({'event':'error','details':{'message':str(exc),'code':exc.code}}),flush=True)
        return exc.code


if __name__=='__main__':raise SystemExit(main())
