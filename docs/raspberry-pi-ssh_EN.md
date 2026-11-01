# Install the complete project and launch over SSH

[中文](raspberry-pi-ssh.md) · [Demo catalog](../demos/README.md) · [Standard commands](standard-app.md)

Version0.10.0 separates same/different-content code and round/square showcases. Configure the driver board's complete HDMI signal first; this app never changes EDID, timings, resolution or touch mapping.

## Initial installation

Use Raspberry Pi OS Bookworm Desktop/labwc. Keep a Wayland desktop logged in as the same ordinary SSH user. SSH login alone is not a graphical session. Substitute your Pi address, then:

```bash
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
./app info --json
```

Square same-content requires0.10.0 or a later compatible version. Only missing system Python/GTK/Cairo/layer-shell/wlr-randr packages are installed. APT may request sudo, but do not launch app as root. No browser, pip, Pygame or virtual environment is required for the standard path.

## Upgrade an existing installation

First stop the old version on the Pi:

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
```

Stop a second instance separately if present. Git installations can then git pull --ff-only and rerun setup. Preserve local edits and a backup; do not force-reset or overwrite running code.

For a development copy, run from the complete local repository:

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets ./ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
```

Include common, scenes, demos, scene_app, scripts and screen-app.json. Copying one scene directory is insufficient. Old leftover files are not registered as canonical layouts. Keep passwords and private configuration out of the public repository.

## Choose a showcase

| Family | Entry | Use cases |
| --- | --- | --- |
| Same / round | ./demos/same/round/demo | Music, RGB lighting, clock |
| Same / square | ./demos/same/square/demo | Retail offers, room availability, parcel pickup |
| Different / round | ./demos/different/round/demo | Flight, automotive, PC case |
| Different / square | ./demos/different/square/demo | Smart home, PC case, industrial pump |

Each directory has independent installation instructions. Every chapter introduces the brand and use case for3s, then runs effects for10s;39s loop. Same-content introductions/effects are identical. Different-content introductions use brand/icon on the left and use-case copy on the right.

Example square same-content:

```bash
cd ~/apps/lvgl-embedded-gui-demos
./demos/same/square/demo check --port 1
./demos/same/square/demo start --port 1
```

Default --signal clone sends one480×480 frame duplicated by hardware. Add --signal sbs to both commands for960×480 SBS boards. Different-content scripts always use SBS. --size 480/720/800 describes each panel; full input is size×size for clone or2×size wide by size high for SBS. Supporting hardware is required.

Square same-content480 clone profiles in0.10.1 accept60Hz and the newly observed~62.811Hz; other square layouts remain60Hz. Physical observation is separate. Round480 clone profiles in0.10.2 accept60/~62.811/~71.295Hz; round480 SBS accepts60/~62.825Hz. Scale1 and normal output rotation are required. port1/2 mapsHDMI-A-1/2 (Pi4 boardHDMI0/1), not the two panels. Two panels share one cable.

## Manage the running app

```bash
./demos/same/square/demo status --port 1
./demos/same/square/demo logs --port 1 --follow
./demos/same/square/demo restart --port 1
```

start waits for data, surface drawing and correct monitor binding, then stays in the background after SSH exits while the desktop remains logged in. Ctrl+C in logs stops viewing only. Restart uses saved settings; stop and recheck/start after a board change. Stop separately:

```bash
./app stop --port 1
```

Same-app/same-version replacement requires explicit --replace and attempts rollback on failure. Stop an old version before updating. Other projects holding the connector must stop through their own normal command; no unrelated PIDs are killed. No boot service is installed.

## Troubleshooting

A missing/ambiguous Wayland session requires logging in to the desktop or explicitly selecting the actual socket for that user. Do not guessDISPLAY=:0 or use ssh -X. Wrong input geometry, refresh, rotation or scale is rejected rather than stretched. clone and SBS are not interchangeable. Panel dimensions alone do not establish board compatibility.

If optional screen-test owns the output, stop it first with screen-test stop --screen 1. pi-setting is not a dependency. Saved layout/app contexts remain version checked; explicitly start the installed layout after an upgrade.

For one dark physical panel, inspect power, driver-board connections and panel cables. One logical output is expected for hardware clone, and a software screenshot cannot prove both physical panels received the signal.

Showcases use labeled simulated values, without audio capture/playback, real weather, prices, calendars or shipment data. Explicit real PC telemetry uses the[PC guide](pc-monitor.md). See[verification](verification.md) for hardware limits. This0.10.0 release was implemented and tested locally after displays were disconnected; the Pi was not connected, updated or started this turn.
