"""Strict standard features and explicit single-link dual-panel layouts."""
import hashlib
import json
import math
import os
from pathlib import Path
import stat

from . import APP_ID, VERSION
from .errors import AppError

ROOT = Path(__file__).resolve().parents[1]
from scenes.registry import SCENES, DEFINITIONS, LAYOUTS, definition

LAYOUT_IDS = tuple(LAYOUTS)


def read_json(path, limit=65536):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError()
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise ValueError()
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError()
        return value, hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, TypeError):
        raise AppError('Cannot read a valid bounded JSON configuration object.', 6) from None


def manifest():
    return json.loads((ROOT / 'screen-app.json').read_text())


def load_layout(layout_id):
    if layout_id not in LAYOUT_IDS:
        raise AppError('Unknown SBS layout. Use ./app info --json for supported IDs.', 3)
    scene, expected_size = LAYOUTS[layout_id]
    data, _ = read_json(ROOT / scene.layout_path(expected_size))
    def require(condition):
        if not condition:
            raise ValueError('Incompatible layout')
    try:
        require(scene.topology in ('single-link-dual','single-link-clone'))
        require(data['layout_version'] == 1 and data['topology'] == scene.topology)
        expected_version = scene.layout_version(expected_size)
        require(data['id'] == layout_id and data['version'] == expected_version)
        require(data['verification']['status'] == 'software-verified')
        require(data.get('content_mode','different') in scene.content_modes)
        if scene.topology=='single-link-clone':
            require(data.get('content_mode')=='same' and scene.shapes[0]==scene.shapes[1])
        signal = data['signal_mode']; viewport = data['viewport']; panels = data['panels']
        size = signal['height']
        require(size == expected_size and signal['width'] == size * scene.input_columns and signal['refresh_hz'] == 60)
        expected_rates = scene.rates(expected_size)
        require(signal.get('accepted_refresh_hz', [signal['refresh_hz']]) == expected_rates)
        require(viewport == {'width': size*scene.input_columns, 'height': size, 'scale': 1, 'rotation_deg': 0})
        require(len(panels) == 2)
        for index, (panel, shape) in enumerate(zip(panels, scene.shapes)):
            require(panel['panel'] == index+1 and panel['shape'] == shape and panel['input'] == 'none')
            require(panel['view'] == scene.panel_ids[index])
            require(panel['rect'] == {'x': index*size if scene.input_columns==2 else 0, 'y': 0, 'width': size, 'height': size})
            require(panel['visual_rotation_deg'] == 0 and panel['safe_inset_percent'] == 0)
    except (ValueError, KeyError, TypeError):
        raise AppError('Installed layout schema/geometry is incompatible.', 6) from None
    return data


def expand(value, count, allowed):
    parts = value.split(',') if isinstance(value, str) else value
    if not isinstance(parts, list) or len(parts) not in (1, count) or any(v not in allowed for v in parts):
        raise AppError('Supply one feature value or exactly one value per panel.', 2)
    return parts*count if len(parts) == 1 else parts


def normalize(values):
    port, count = values.get('port'), values.get('panels', 1)
    if type(port) is not int or port not in (1, 2) or type(count) is not int or count not in (1, 2):
        raise AppError('Use --port 1/2 and --panels 1/2.', 2)
    shapes = expand(values.get('shape'), count, ('round','square','rect','strip'))
    inputs = expand(values.get('input','none'), count, ('touch','none'))
    if count != 2 or inputs != ['none','none']:
        raise AppError('This project supports two panels without touch interaction.', 3)
    layout_id=values.get('layout')
    layout=load_layout(layout_id)
    scene,_=LAYOUTS[layout_id]
    view=values.get('view') or scene.id
    if view not in DEFINITIONS or view != scene.id or shapes != list(scene.shapes):
        raise AppError('The shape, view and layout must belong to the same scene. See ./app info --json.', 3)
    content=values.get('content')
    if content not in scene.content_modes or content!=layout.get('content_mode','different'):
        raise AppError(f'{view} requires --content '+layout.get('content_mode','different')+'.',3)
    source=values.get('data_source','demo')
    if source not in ('demo','live'):
        raise AppError('Use --data-source demo or live.',2)
    if source not in scene.sources:
        raise AppError(f'{view} currently supports demo data only.',3)
    requested_version = values.get('layout_version', layout['version'])
    if requested_version != layout['version']:
        raise AppError('Saved layout version changed; start the new layout explicitly.', 6)
    config = values.get('config')
    if config is not None and not isinstance(config, str):
        raise AppError('Configuration path must be text.', 6)
    return {'contract_version':1,'app_id':APP_ID,'app_version':VERSION,'port':port,'panels':2,
            'shape':shapes,'input':inputs,'topology':scene.topology,'profile_id':scene.profile_id,
            'view':view,'content':content,'layout':layout['id'],'layout_version':layout['version'],
            'data_source':source,'config':str(Path(config).expanduser().resolve()) if config else None}


def context(path):
    try:
        st = Path(path).stat()
        if st.st_uid != os.getuid() or st.st_mode & 0o077 or not stat.S_ISREG(st.st_mode):
            raise ValueError()
    except (OSError, ValueError):
        raise AppError('Context must be a private regular file owned by this user.', 6) from None
    data, _ = read_json(path)
    if (data.get('contract_version') != 1 or data.get('app_id') != APP_ID or data.get('app_version') != VERSION
            or data.get('owner',os.getuid()) != os.getuid()):
        raise AppError('Incompatible context/app identity or version.', 6)
    return normalize(data)


def prepare(spec):
    config, digest = ({'config_version':1,'fps':30,'demo_speed':1.0}, 'default')
    if spec['config']:
        supplied, digest = read_json(spec['config'])
        if supplied.get('config_version') != 1 or set(supplied) - {'config_version','fps','input_file','demo_speed'}:
            raise AppError('Use config_version 1 with fps, demo_speed and optional input_file.', 6)
        config.update(supplied)
    if type(config['fps']) is not int or not 10 <= config['fps'] <= 60:
        raise AppError('fps must be an integer from 10 to 60; this is rendering, not HDMI refresh.', 6)
    speed=config['demo_speed']
    if type(speed) not in (int,float) or not math.isfinite(speed) or not .25<=speed<=4:
        raise AppError('demo_speed must be a finite number from 0.25 to 4.',6)
    path = None
    if spec['data_source'] == 'live':
        value = config.get('input_file')
        if not isinstance(value, str) or not value:
            raise AppError('Live mode requires input_file in --config.', 8)
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = Path(spec['config']).parent / path
        path = path.resolve()
    # Demo explicitly ignores configured input_file; no implicit live source.
    source=definition(spec['view']).create_source(spec['data_source'],path)
    if getattr(source,'requires_real_time',False) and speed!=1:
        raise AppError('Product-presentation durations use wall time; demo_speed must be 1.',6)
    source_digest=getattr(source,'configuration_digest',None)
    if source_digest is not None:
        digest=hashlib.sha256((digest+':'+source_digest).encode()).hexdigest()
    return config, digest, source
