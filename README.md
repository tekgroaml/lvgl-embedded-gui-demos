# Embedded Instrumentation & Gauge Demos

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Renderer](https://img.shields.io/badge/renderer-Pygame%202-green) ![Input](https://img.shields.io/badge/telemetry-JSON-orange)

[简体中文](README_CN.md)

A circular automotive speedometer/tachometer and a square industrial panel for small HDMI screens. Despite the repository's historical `lvgl-embedded-gui-demos` name, **the delivered renderer is Pygame, not LVGL or Python-LVGL bindings**. This follows the Python/Pygame stack option and avoids platform-specific LVGL binding builds on Pi. The data/render boundary is designed to be portable to an LVGL application later.

![Software preview](docs/preview.png)

## Files

```text
lvgl-embedded-gui-demos/
├── docs/
│   └── preview.png
├── examples/
│   └── telemetry.json
├── gauges/
│   ├── __init__.py
│   ├── automotive_gauge.py
│   ├── common.py
│   └── industrial_panel.py
├── tests/
│   └── test_telemetry.py
├── .gitignore
├── README.md
├── README_CN.md
├── requirements.txt
├── run.sh
└── setup.sh
```

## Hardware and setup

With power off, connect Pi HDMI0 to the display driver HDMI input (micro-HDMI on Pi 4/5); supply both Pi and driver with their specified power. USB touch/data is optional here. Configure native 480×480 or 720×720 and 100% desktop scaling with the companion hardware guide. The circular automotive UI stays inside the round aperture; the industrial panel uses square corners and is intended for square displays.

On Raspberry Pi OS Bookworm/Bullseye desktop or Debian with a working Wayland/X11 desktop:

```bash
chmod +x setup.sh run.sh
./setup.sh                       # Installs and launches automotive fullscreen
./setup.sh industrial            # Installs and launches industrial fullscreen
./setup.sh --install-only
./run.sh automotive
./run.sh industrial --size 720 --fps 30
./run.sh automotive --windowed   # Development monitor
```

APT installs Debian's Pygame/SDL. A `--system-site-packages` venv uses that build; the pinned `requirements.txt` (Pygame 2.6.1) is a pip fallback if the system module is unavailable. Debian's version can be an older 2.x release. No global pip modification, external fonts, image assets, OpenGL binding or network service is needed. Run as the desktop user without sudo. Fullscreen checks the desktop size; it does not change HDMI timings or set up direct DRM console rendering.

You can also launch the requested entry files directly using the venv Python:

```bash
.venv/bin/python gauges/automotive_gauge.py --windowed
.venv/bin/python gauges/industrial_panel.py --windowed
```

## Instruments and controls

The automotive view combines a 0–300 km/h scale, a 0–8,000 RPM ring, an animated rim needle, digital speed/RPM, temperature and voltage. Needles ease toward telemetry using elapsed time. Redline starts at 6,500 RPM; coolant warning starts at 95 °C. The simulation repeatedly sweeps values through the scales and alerts.

The industrial view shows a normalized waveform, link/warning/fault LEDs and temperature, pressure, bus voltage and shaft speed. The waveform stores 180 samples at 30 Hz (six seconds), independent of rendering FPS. Input JSON is polled at 5 Hz and held between updates: this display is **not a hardware oscilloscope or a 30 Hz acquisition device**. Invalid/stale samples create gaps rather than fabricated waveforms. Pressure warning starts at 8 bar; low voltage at 11 V.

| Key / option | Behavior |
| --- | --- |
| Esc / `Q` | Exit |
| Space | Pause/resume simulation only; live input is never frozen by this key |
| Tab | Switch between views on a single panel |
| `--fps 30` | Reduce rendering load |
| `--display N` | Select physical SDL display N |
| `--sbs` | One wide window: automotive on A/left, industrial on B/right |
| `--frames N --screenshot PATH` | Bounded run and final PNG |

For a dual 480×480 board:

```bash
./run.sh automotive --sbs --size 480
```

Configure the desktop as **960×480**, keep 100% scaling and no combined rotation. The board's one HDMI port receives one SBS canvas; two square surfaces map to A and B. This is not two extended-desktop outputs. `--size 720 --sbs` requires a board and desktop that actually support 1440×720. `--sbs` fixes the two views, so Tab has no effect on their positions.

## Real telemetry through JSON snapshots

```bash
./run.sh automotive --windowed --input-file examples/telemetry.json
```

The sample is a static contract example and becomes **DATA STALE** once its file modification time is more than three seconds old. A real adapter must publish fresh atomic snapshots at least once every three seconds, preferably 5 Hz. All six finite numeric fields are required:

| Field | Unit / accepted range |
| --- | --- |
| `speed` | km/h, 0–300 |
| `rpm` | RPM, 0–9,000 (visual ring saturates at 8,000) |
| `temperature` | °C, −40–150 |
| `pressure` | bar, 0–20 |
| `voltage` | V, 0–60 |
| `signal` | normalized amplitude, −1–1 |

`TelemetrySource` reads at most 64 KiB, rejects missing/nonfinite/out-of-range fields, keeps the last valid values on failure and marks them stale. It never silently switches a failed live feed to simulation. Keep the Pi clock correct; file freshness uses wall-clock modification time. Publish using a temporary file on the **same filesystem** followed by `os.replace`:

```python
import json
import os
from pathlib import Path

def publish_snapshot(destination, values):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(values, allow_nan=False))
    os.replace(temporary, destination)
```

Use one writer per destination. This helper expects the complete field dictionary shown in `examples/telemetry.json`; the acquisition adapter supplies real measurements. Rendering stays on the main thread; keep serial/Bluetooth/USB reads in a separate process and never block the GUI waiting for an ECU or PLC.

## OBD-II, industrial and LVGL adaptation

For OBD-II, a separate adapter can use `python-obd` with a compatible ELM327 device, obtain speed/RPM/coolant/voltage when supported, convert units explicitly and publish validated snapshots. Pressure and normalized signal must come from an actual available sensor or be mapped deliberately; do not label fabricated values as live. Missing PIDs should cause an unavailable/stale indication, and protocol requests need timeouts/reconnect handling. This repository does not ship an OBD-II driver or transmit vehicle commands. Use the demo for bench prototyping; driving instrumentation requires independent qualification.

For industrial telemetry, use a separate Modbus/MQTT/serial adapter with known engineering units, bounds and sampling timestamps; map it into the same contract or extend `Telemetry` and validation. The built-in alert thresholds are examples, not certified control or protection logic.

For an LVGL port, keep acquisition/validation separate; replace `Painter` and the view draw methods with LVGL scale/arc/label/chart objects, update them from the LVGL event/timer loop, and retain the single framebuffer SBS split where applicable. LVGL on an MCU additionally requires a real display/input driver, flush callback, color format and memory budget. Python-LVGL bindings are not included or implied by this repository name.

## Headless checks and troubleshooting

```bash
./run.sh automotive --headless --frames 180 --screenshot /tmp/automotive.png
./run.sh industrial --headless --frames 180 --screenshot /tmp/industrial.png
./run.sh automotive --sbs --headless --frames 180 --screenshot /tmp/sbs.png
```

Headless runs use SDL's dummy driver and fixed simulation time steps. They validate drawing and lifecycle, not real Pi performance, HDMI timing or panel splitting.

| Problem | Action |
| --- | --- |
| Fullscreen size rejected | Configure native square/wide desktop resolution or pass `--windowed`. |
| Waveform flat/stale | Check `signal` values, atomic updates, file permissions and the three-second freshness window. |
| Industrial labels clipped on a round screen | Use a square panel or adapt the tile layout into the circular safe area. |
| Low FPS | Use `--fps 30`, close background effects and check thermal throttling. |
| Pygame or display error | Run setup, use `run.sh`, and launch inside your desktop without sudo. |
| Swapped SBS panels | Check controller A/B cable order, scale and exact canvas dimensions. |

Hardware, real sensor integration and deployment on a specific Pi still require validation on that system.

## Developer verification

```bash
python3 -m unittest discover -s tests -v
```

The 3 standard-library tests cover the core configuration, behavior or input/API boundary. The development verification used macOS, not Raspberry Pi hardware. Shell syntax and Python compilation were checked; the interactive demos were rendered where applicable. APT installation and the actual Pi boot/desktop still require on-device checks.

Older Bullseye images may provide Pygame 1.x. In that case setup installs SDL2/build prerequisites and builds the pinned Pygame 2 fallback if no wheel is available; allow extra installation time and disk space.
