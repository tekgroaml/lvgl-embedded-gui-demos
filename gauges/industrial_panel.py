"""Compatibility import; scene code moved to scenes/different/automotive_industrial/industrial_panel.py."""
if __package__ in (None, ''):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scenes.different.automotive_industrial.industrial_panel import IndustrialPanel

if __name__ == '__main__':
    from gauges.common import run
    raise SystemExit(run('industrial'))
