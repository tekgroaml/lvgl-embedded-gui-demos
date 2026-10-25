# Copy the single-cable dual-panel instruments to a Pi and launch over SSH

[中文](raspberry-pi-ssh.md) · [Project README](../README.md)

This guide is independent of the parent application repository and pi-setting. Copy app files, not a new operating-system image.

The current executable is run.sh; the standardized ./app interface has not been added to this project. The actual renderer is Pygame. SBS draws automotive instruments on the left and an industrial panel on the right in one wide frame. Same-content mode and touch interactions are not implemented.

## 1. Prepare the Pi

This guide targets Raspberry Pi OS Bookworm Desktop with labwc/Wayland. Enable SSH and log the intended user into the actual desktop. SSH alone does not create that desktop.

For the dual 480×480 software mode, the selected desktop must be 960×480 at 100% scale with no whole-canvas rotation. Confirm that the driver board really accepts and splits that input; do not infer its timing only from panel dimensions. The industrial page uses square corners and may be clipped on a round physical panel.

Replace pi@raspberrypi.local below with the real user and hostname/IP. Verify the SSH fingerprint and authenticate normally. Mac commands upload files; subsequent install/session/run commands execute in the Pi SSH shell.

## 2. Mac terminal: upload and connect

Enter the parent directory containing lvgl-embedded-gui-demos:

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets lvgl-embedded-gui-demos/ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
ssh pi@raspberrypi.local
```

Copy the full project, not an isolated gauge.py. Do not copy the Mac virtual environment: install Pi-native dependencies.

Alternatively, after installing git on the Pi, clone the published repository into a nonexistent destination:

```bash
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/apps
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
```

Do not clone over an existing upload. Unpublished local changes cannot be obtained from GitHub.

## 3. Pi SSH terminal: install only

```bash
cd ~/apps/lvgl-embedded-gui-demos
chmod +x setup.sh run.sh
./setup.sh --install-only
.venv/bin/python -c 'import pygame; print(pygame.version.ver)'
```

The installer uses sudo for APT and creates a Pi-local virtual environment, falling back to the pinned Pygame version when needed. Do not run the application with sudo. Omitting --install-only starts the old single-panel default immediately.

## 4. Pi SSH terminal: select the actual desktop

This project does not yet discover SSH graphical sessions automatically. List real sockets:

```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
python3 - <<'PY'
import os
from pathlib import Path
for item in sorted(Path(os.environ['XDG_RUNTIME_DIR']).glob('wayland-*')):
    if item.is_socket():
        print(item.name)
PY
```

Use the following only if wayland-0 is the intended socket; otherwise replace it with the actual name. Multiple sessions require selection; no socket means you must first log into the desktop.

```bash
export WAYLAND_DISPLAY=wayland-0
export SDL_VIDEODRIVER=wayland
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
.venv/bin/python - <<'PY'
import pygame
pygame.display.init()
for index, size in enumerate(pygame.display.get_desktop_sizes()):
    print(index, size)
pygame.display.quit()
PY
```

Below assumes you confirmed SDL index 0 is the 960×480 target. --display is a zero-based SDL index, not a Linux HDMI number. Do not convert port numbers by subtracting one. Identical-size outputs cannot be reliably mapped to connectors by the current launcher; verify manually, or initially connect only the product under test.

No ssh -X or guessed DISPLAY=:0 is needed. X11 requires separately verified DISPLAY/XAUTHORITY and is outside this Wayland procedure.

## 5. Pi SSH terminal: test foreground output

```bash
./run.sh automotive --sbs --size 480 --display 0
```

Confirm left/right contents and complete edges. Ctrl+C or a focused Esc/Q key exits. This foreground method does not promise survival after SSH disconnects.

--size 720 requires 1440×720 hardware/desktop support. --fps 30 limits rendering; it does not configure the HDMI refresh rate. Without --input-file, telemetry is simulated.

## 6. Pi SSH terminal: continue after SSH disconnects

First exit the foreground test. In the same project directory and SSH shell with the verified variables, launch a transient user service:

```bash
systemd-run --user --unit=tekgroaml-instruments --collect --property=Type=exec --property="WorkingDirectory=$PWD" --setenv="XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR" --setenv="WAYLAND_DISPLAY=$WAYLAND_DISPLAY" --setenv="SDL_VIDEODRIVER=$SDL_VIDEODRIVER" --setenv="DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS" "$PWD/run.sh" automotive --sbs --size 480 --display 0
```

This uses existing user systemd facilities, not a new ./app command or autostart implementation. Returning means the process executed, not that the frame was visually verified. It can keep running after SSH disconnects while the desktop user remains logged in.

```bash
systemctl --user status tekgroaml-instruments.service
journalctl --user -u tekgroaml-instruments.service -n 50 --no-pager
journalctl --user -u tekgroaml-instruments.service -f
```

Ctrl+C exits log following only. To stop:

```bash
systemctl --user stop tekgroaml-instruments.service
```

--collect allows the inactive transient unit to disappear; historical journal entries remain. Re-run systemd-run to launch again, after the previous unit has stopped. Do not use killall python. This procedure does not install reboot autostart or promise recovery after desktop logout.

## 7. Updates and failures

Stop this service and foreground instances before uploading updates. Repeat the Mac rsync, enter the Pi project, reinstall if dependencies changed and recheck session/display selection.

- Missing Pygame/.venv: install on the Pi rather than uploading a Mac environment.
- No video device: verify the same desktop user, actual Wayland socket and SDL backend.
- Wrong dimensions: verify selected SDL output, scale, board input and exact960×480/1440×720 canvas.
- Cropped/swapped content: check board A/B mapping; the industrial view is square.
- Unit already exists: inspect and stop it before relaunching.
- User systemd bus unavailable: use the normal logged-in desktop user and a working user systemd/DBus session.
- Stale JSON telemetry: verify the real adapter's complete, continuously updated atomic snapshots; the bundled JSON is not a sampler.

Optional software-only check, which does not show on a physical monitor:

```bash
./run.sh automotive --sbs --headless --frames 180 --screenshot /tmp/instruments-sbs.png
```

See README for telemetry protocol details. Hardware timing, physical board splitting and specific Pi deployment still need actual verification.
