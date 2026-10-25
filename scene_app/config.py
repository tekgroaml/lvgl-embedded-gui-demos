"""Strict standard features and explicit single-link dual-panel layouts."""
import hashlib
import json
import os
from pathlib import Path
import stat

from . import APP_ID, VERSION
from .errors import AppError

ROOT = Path(__file__).resolve().parents[1]
LAYOUT_IDS = tuple(f'automotive-industrial-sbs-{size}' for size in (480, 720, 800))


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
    data, _ = read_json(ROOT / 'layouts' / (layout_id + '.json'))
    def require(condition):
        if not condition:
            raise ValueError('Incompatible layout')
    try:
        require(data['layout_version'] == 1 and data['topology'] == 'single-link-dual')
        require(data['id'] == layout_id and data['version'] == '1.0.0')
        require(data['verification']['status'] == 'software-verified')
        signal = data['signal_mode']; viewport = data['viewport']; panels = data['panels']
        size = signal['height']
        require(size in (480, 720, 800) and signal['width'] == size * 2 and signal['refresh_hz'] == 60)
        require(viewport == {'width': size*2, 'height': size, 'scale': 1, 'rotation_deg': 0})
        require(len(panels) == 2)
        for index, (panel, shape) in enumerate(zip(panels, ('round', 'square'))):
            require(panel['panel'] == index+1 and panel['shape'] == shape and panel['input'] == 'none')
            require(panel['rect'] == {'x': index*size, 'y': 0, 'width': size, 'height': size})
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
    if count != 2 or shapes != ['round','square'] or inputs != ['none','none']:
        raise AppError('This scene supports two panels: left round, right square, no touch.', 3)
    if values.get('content') != 'different':
        raise AppError('Specify --content different; same-content mode is not implemented.', 3)
    view = values.get('view') or 'automotive-industrial'
    source = values.get('data_source','demo')
    if view != 'automotive-industrial':
        raise AppError('Only the automotive-industrial composite view is supported.', 3)
    if source not in ('demo','live'):
        raise AppError('Use --data-source demo or live.', 2)
    layout = load_layout(values.get('layout'))
    requested_version = values.get('layout_version', layout['version'])
    if requested_version != layout['version']:
        raise AppError('Saved layout version changed; start the new layout explicitly.', 6)
    config = values.get('config')
    if config is not None and not isinstance(config, str):
        raise AppError('Configuration path must be text.', 6)
    return {'contract_version':1,'app_id':APP_ID,'app_version':VERSION,'port':port,'panels':2,
            'shape':shapes,'input':inputs,'topology':'single-link-dual','profile_id':'sbs-automotive-industrial',
            'view':view,'content':'different','layout':layout['id'],'layout_version':layout['version'],
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
    from gauges.common import TelemetrySource
    config, digest = ({'config_version':1,'fps':30}, 'default')
    if spec['config']:
        supplied, digest = read_json(spec['config'])
        if supplied.get('config_version') != 1 or set(supplied) - {'config_version','fps','input_file'}:
            raise AppError('Use config_version 1 with fps and optional input_file.', 6)
        config.update(supplied)
    if type(config['fps']) is not int or not 10 <= config['fps'] <= 60:
        raise AppError('fps must be an integer from 10 to 60; this is rendering, not HDMI refresh.', 6)
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
    return config, digest, TelemetrySource(path)
