# Single-cable dual-panel instrumentation demos

**v0.2.0 software preview.** A standard ./app entrypoint now renders the existing automotive and industrial views with native Python/GTK3/Cairo. No browser, WebKit, LVGL, Pygame, pip or virtual environment is required by this path. Legacy Pygame scripts remain optional.

![Native SBS offscreen preview](docs/preview-native-sbs.png)

[中文](README_CN.md) · [Copy to Pi and run over SSH](docs/raspberry-pi-ssh_EN.md) · [Command reference](docs/standard-app.md) · [Telemetry protocol](docs/telemetry_EN.md) · [Verification](docs/verification.md)

## Standard launch

On Raspberry Pi OS Bookworm Desktop/labwc, as the normal user who owns the logged-in Wayland session:

```bash
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
./app info --json
./app check --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
./app status --port 1
./app logs --port 1 --follow
./app stop --port 1
```

Use port2 consistently if wired to HDMI-A-2; port1 is HDMI-A-1 (Pi4 board HDMI0), port2 is HDMI-A-2 (board HDMI1). Two panels share one HDMI canvas, not two connector instances. The profile is **left round/right square, no touch, different content**. Single-panel, dual-round, touch and same-content requests are rejected.

| Explicit software layout | Full input canvas at 60Hz | Each panel |
| --- | --- | --- |
| automotive-industrial-sbs-480 | 960×480 | 480×480 |
| automotive-industrial-sbs-720 | 1440×720 | 720×720 |
| automotive-industrial-sbs-800 | 1600×800 | 800×800 |

These mappings describe software geometry, not a certified driver-board product. Confirm the actual full input mode and left/right splitting first. The industrial view uses square corners and is not round-safe. Normal rotation and100% scale are required; no timing, resolution, EDID or USB mapping is changed.

## Minimal runtime and lifecycle

setup.sh only installs missing distribution Python/GTK/Cairo/layer-shell/wlr-randr packages and never launches the application. Existing dependencies require no download. Use the ordinary desktop user, without sudo for app commands.

SSH discovers the same user's unique active Wayland session. The app matches the connector geometry to a unique monitor and binds its layer-shell surface explicitly; SDL enumeration is not used. Ambiguous mirrored geometry and unsupported modes are rejected.

start supervises a background run, returning only after actual drawing, data readiness and output binding. It can continue after SSH disconnects while the desktop remains logged in. Ctrl+C in logs only stops following logs. run is the foreground debug alternative; restart uses saved settings. Per-user connector locks and private control sockets prevent other projects from being stopped or replaced accidentally. No reboot autostart is installed.

The optional screen-test tool can run first: stop any current app, run tap-cycle, physically observe, then stop that test and start the app. Neither screen-test nor pi-setting is required.

## Demo and live

Demo is explicit and ignores any configured input file. Live uses --data-source live --config <file>, with examples/live.json specifying config_version=1, fps and input_file. Relative data paths resolve next to the configuration. Rendering fps 10–60 is separate from HDMI refresh.

A real adapter must atomically update complete validated snapshots; the example telemetry JSON is static and becomes stale after three seconds. Missing/invalid/stale data never turns into demo. Initial live readiness requires a fresh valid snapshot; later failures retain last values, show DATA STALE and report degraded health. Background file reads do not block GTK drawing. This application reads telemetry only, sends no hardware control commands and is not an automotive or industrial protection system.

## Legacy and validation

./setup.sh --legacy-pygame installs optional legacy dependencies and creates the Pi-local .venv used by ./run.sh automotive --sbs --size 480. The legacy renderer uses zero-based SDL --display indexes, not Linux connector numbers. Stop an old tekgroaml-instruments.service before using the new interface.

scene_app contains the CLI, lifecycle, configuration, output matching and Cairo painter; gauges preserves existing view/telemetry logic, layouts holds versioned SBS maps, and tests covers the standard contract and data/lifecycle regressions.

25 tests passed on the development Mac; the 24-test base suite also passed in a temporary Pi directory. Actual Cairo offscreen rendering passed at960×480/1440×720/1600×800. The new on-screen dual-panel surface, physical driver-board mapping and long-duration performance remain unverified. See the self-contained SSH guide and verification record.
