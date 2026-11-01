# Copy the dual-panel application to a Pi and operate it over SSH

[中文](raspberry-pi-ssh.md) · [README](../README.md) · [Command details](standard-app.md)

This guide is self-contained. Copy application files, not a new TF-card image. No parent application repository, round-screen app, pi-setting or global screen-app is required.

## 1. Prerequisites and terminal locations

Use Raspberry Pi OS Bookworm Desktop/labwc with SSH enabled and the intended user already logged into the Wayland desktop. SSH/console login alone does not create that session. Configure the driver board's actual full input mode and panel splitting first, at 100% scale and normal rotation.

The supported profile is left round automotive / right square industrial, two panels on one HDMI, no touch and different content. For the 480 layout, software requires 960×480@60; physical board support is not inferred from panel dimensions. Dual-round now uses the dedicated flight view; dual-square uses the dedicated industrial pump view. Touch and same-content are not implemented.

Replace pi@raspberrypi.local with your real username and hostname/IP. Verify the host fingerprint and authenticate normally; do not put passwords in commands. Upload/SSH commands run on the Mac, then installation and app commands run inside the Pi SSH shell.

## 2. Mac terminal: upload and log in

Enter the parent directory containing lvgl-embedded-gui-demos:

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets lvgl-embedded-gui-demos/ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
ssh pi@raspberrypi.local
```

Copy the full app, scene_app, common, scenes, demos, gauges and screen-app.json, not one Python file. Do not upload a Mac virtual environment. Keep private capture data/configuration elsewhere in the Pi home directory.

For already-published versions, Git is an alternative to the upload. On the Pi, with a nonexistent target directory:

```bash
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/apps
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
```

Do not clone over an existing upload. Unpublished local changes require copying; git pull cannot retrieve them.

## 3. Pi SSH terminal: install and inspect

```bash
cd ~/apps/lvgl-embedded-gui-demos
chmod +x app setup.sh run.sh
./setup.sh --install-only
./app --version
./app info --json
```

This native preview is 0.6.1. Only missing distribution Python/GTK/Cairo/layer-shell/wlr-randr packages are installed; existing dependencies need no download. No Pygame, browser, pip, compilation or virtual environment is required. The installer may use sudo for APT; never use sudo for ./app.

If you previously launched the old transient service, stop it before the standard app:

```bash
systemctl --user stop tekgroaml-instruments.service
```

Skip that if no old service exists; also exit any foreground legacy run.sh. The new preflight detects the old service rather than silently competing with it.

## 4. Pi SSH terminal: check and start

Assuming the real driver input is 960×480@60 and wired to connector 1:

```bash
./app check --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
```

Port 1/2 means Linux HDMI-A-1/2 (Pi4 board HDMI0/1); change all port arguments together if using connector 2. panels 2 means two regions inside this one output, not two HDMI cables.

For software 720/800 layouts choose automotive-industrial-sbs-720/800, requiring 1440×720@60 or 1600×800@60 respectively. These are explicit software mappings, not certified physical products. Mode mismatch is rejected without changing timings, EDID, scaling or rotation.

The app discovers this user's unique actual Wayland session. It no longer needs SDL --display or a .venv. For multiple sessions, list actual sockets:

```bash
python3 - <<'PY'
import os
from pathlib import Path
for item in sorted((Path('/run/user')/str(os.getuid())).glob('wayland-*')):
    if item.is_socket():
        print(item.name)
PY
```

Select the intended name explicitly if needed, for example export WAYLAND_DISPLAY=wayland-0 only when that is the real target. If no socket exists, log into the desktop first. Do not guess DISPLAY=:0 or use ssh -X.

### Dedicated dual-round and dual-square views

Choose one mode after stopping the previous instance on this output. Both examples use a verified-by-you 960×480 full input for two480 panels:

```bash
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view flight --layout flight-sbs-480 --content different --data-source demo
```

Switch to the square pump-station demo:

```bash
./app stop --port 1
./app start --port 1 --shape square --panels 2 --input none --view industrial --layout industrial-sbs-480 --content different --data-source demo
```

These demo-only views move autonomously using correlated scene data, not random independent needles. Both also have720/800 software mappings. See the [scenario reference](scenarios.md) for phase timing and optional demo_speed acceleration.

### Dual-round automotive (v0.4.0)

After stopping the previously running version, copy/update the complete project including common/ and scenes/. Existing layout IDs remain stable even though layout files moved into each scene directory. Then on the Pi:

```bash
./app --version
./app check --port 1 --shape round --panels 2 --input none --view automotive --layout automotive-sbs-480 --content different --data-source demo
./app start --port 1 --shape round --panels 2 --input none --view automotive --layout automotive-sbs-480 --content different --data-source demo
```

The dedicated car view displays speed/RPM/gear/trip and coolant/fuel/voltage/oil pressure. It automatically cycles through realistic linked showroom states, always marked simulated, and explicitly rejects live/OBD. Its480 layout accepts60Hz and the observed~62.825Hz. No display timing is changed. See [car details](automotive.md) and [directory architecture](architecture.md).

## 5. Manage and disconnect SSH

```bash
./app status --port 1
./app logs --port 1 --follow
```

Ctrl+C exits log following only. Then:

```bash
./app restart --port 1
./app stop --port 1
```

start waits for actual drawing, fresh initial data and output binding, then runs supervised in the background. It can continue after SSH disconnects while the graphical desktop user remains logged in. This does not install reboot autostart or promise recovery after desktop logout.

For foreground debugging, stop the background instance and replace start with run in the same command; Ctrl+C ends it. Do not rely on foreground run surviving disconnect. stop closes both panels on that output but only owns this project's instance. It never uses killall python or terminates other projects.

## 6. Optional screen test before the demo

If the optional screen-test tool is installed, stop the app, run screen-test pattern --screen 1 or cycle, and physically observe the panels. Then:

```bash
screen-test stop --screen 1
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
```

The test flag still names one full HDMI output. It is not a dependency or a per-panel hardware test. If another app owns the connector, stop it through that project's normal command first.

## 7. Data, updates and failures

Only the original automotive-industrial view supports live JSON. New flight/industrial views explicitly reject live. Use --data-source live --config <file> with examples/live.json. input_file resolves relative to that configuration, fps 10–60 affects rendering only. A real collector must continuously publish all six validated fields atomically. The bundled telemetry.json is static and becomes stale after three seconds. Initial invalid/stale data prevents readiness; later failure retains last values with DATA STALE/degraded health, never demo fallback.

Stop this app before updating. Repeat Mac rsync, reconnect, check the installed version, reinstall changed dependencies and run check/start. Preserve the collector and private configuration. Do not overwrite running code and claim old-binary rollback.

- Missing runtime: install on the Pi; do not upload a Mac .venv or run the GUI with sudo.
- No desktop: use the same user who owns a logged-in Wayland session.
- Wrong mode/output: configure the exact full driver input first; the app does not force it.
- Unsupported profile: use a declared shape/view/layout combination; all views remain no-touch and different-content only.
- Occupied output: use the original project's stop; cross-project forced replacement is rejected.
- Old service conflict: stop tekgroaml-instruments.service instead of creating another old systemd-run unit.
- Cropped/swapped physical images: verify board A/B layout, cabling and panel shapes; software PNGs cannot certify it.
- Stale JSON: check the collector's full field set, ranges, timestamps and continuous atomic updates.

## 8. Software checks and legacy path

```bash
python3 -m unittest discover -s tests -v
python3 tests/render_native.py --size 480 --output /tmp/instruments-480.png
```

The offscreen PNG creates no desktop window and does not prove physical splitting. On-screen dual-panel and long-duration acceptance remain pending.

For the retained old renderer explicitly install ./setup.sh --legacy-pygame, then ./run.sh automotive --sbs --size 480. That optional path still uses zero-based SDL display indexes, which are not connector numbers. Standard ./app never launches it. See the telemetry reference for data protocol and hardware-integration boundaries.

Observed product note (2026-11-01): flight-sbs-480 v1.1.0 also accepts the connected dual480 driver input at960×480/~62.825226Hz (±0.1Hz). The native mode is preserved, not forced to60Hz. Full Pi startup was confirmed; inspect physical splitting and edges separately.

## PC-case display (v0.5.0)

After copying the updated project, on the Pi:

```bash
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view pc-monitor --layout pc-monitor-sbs-480 --content different --data-source demo
```

CPU/RAM and GPU/cooling animate automatically in demo. Live uses examples/pc-monitor-live.json and a snapshot from the monitored PC, never Pi host stats. An optional Windows PowerShell collector and key-based SSH upload procedure are documented in the [PC-monitor guide](pc-monitor.md); unsupported sensors remain unavailable. The new scene and Windows collector have not been physically accepted in this change.

## Product showcase recording (v0.6.0)

After updating the complete project including demos/, use this in the Pi SSH shell:

```bash
./app stop --port 1
./demos/product_showcase/demo check --port 1
./demos/product_showcase/demo start --port 1
```

The script loops flight → car/motorcycle → PC-case. Each title/icon lasts3s and each simulated effect10s,39s per loop, in one continuous surface. Later stop with ./demos/product_showcase/demo stop --port 1. See the [independent demonstration guide](../demos/product_showcase/README_EN.md) for copy/timing customization and preview. It does not use real devices or PC telemetry.
