# Three-use-case product showcase

[中文](README.md) · [Full39-second loop preview](preview-loop.gif)

This standalone demonstration directory expresses three product uses: flight-simulator instruments, car/motorcycle instruments and PC-case monitoring. It directly reuses the existing demo models/panels in one native GTK/Cairo surface, not three processes or browser windows.

| Wall time | Content |
| --- | --- |
| 0–3s | Aircraft icon + FLIGHT SIMULATOR title |
| 3–13s | Flight instruments |
| 13–16s | Car/motorcycle icon + CAR / MOTORCYCLE title |
| 16–26s | Dual-round vehicle instruments |
| 26–29s | Tower icon + PC CASE MONITOR title |
| 29–39s | CPU/RAM and GPU/cooling demo |
| 39s | Repeat from the first title |

All data is visibly simulated. The car/motorcycle chapter uses the implemented automotive demo to express an instrument-display use case; it is not a motorcycle ECU integration or fit certification. PC data remains synthetic throughout this marketing presentation.

## Run on the Pi over SSH

Update the entire repository, including demos/, scenes/, common/ and scene_app/, to0.6.1 after stopping the previous app version. In the Pi SSH shell:

```bash
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
./app stop --port 1
./demos/product_showcase/demo check --port 1
./demos/product_showcase/demo start --port 1
```

Port1 meansHDMI-A-1/Pi4 boardHDMI0. Use port2 consistently forHDMI-A-2. Default is two480×480 circular regions in one960×480 output at60Hz or the observed~62.825Hz. Other explicit --size720/800 options require1440×720/1600×800 at60Hz and matching hardware. No signal settings are changed.

The same user must already own a logged-in Wayland/labwc desktop. SSH alone does not create a graphical session. No browser, player, pip or icon-font download is added.

```bash
./demos/product_showcase/demo status --port 1
./demos/product_showcase/demo logs --port 1 --follow
./demos/product_showcase/demo stop --port 1
```

Ctrl+C in logs only stops following. Background start can continue after SSH disconnect while the desktop remains logged in; no reboot autostart is installed. Foreground debugging uses run instead of start. Existing occupancy/ownership rules apply, so another project is never killed to obtain the connector.

## Standard equivalent

```bash
./app start --port 1 --shape round --panels 2 --input none --view product-showcase --layout product-showcase-sbs-480 --content different --data-source demo
```

The wrapper only fills standard arguments. One leased surface remains open across all chapters, avoiding intentional desktop gaps. Status telemetry includes scene, phase, stage_index, cycle_index, phase_duration and the simulated payload.

## Edit copy and pacing

playlist.json owns the titles/subtitles, per-panel role copy, vector-icon names, intro_seconds3, effect_seconds10 and scenario demo offsets. Its digest participates in idempotent launch checks; restart after editing. Default total is39s.

Active seed offsets are35s for flight,28s for automotive and74s for PC. They make a ten-second effect start in an informative moving state instead of idle, without changing title/effect wall time. The first title's clock starts after its first visible ready frame. Actual transitions are quantized to a data/render frame.

Global demo_speed must remain1 for this product presentation; change the playlist durations explicitly if desired. Three supported scene IDs stay in their declared order, with no external commands/live sources. English copy is default; non-Latin customization needs a suitable font already installed on the target Pi.

## Implementation and scope

playback.py implements the timeline, panels.py delegates existing effects and draws title cards, icons.py draws local vectors, scene.py/layouts register the view, and cli.py/demo expose standard management. The directory is independent of ordinary scene implementation while sharing the same lifecycle.

79 unit tests cover schedule boundaries,39s loops, initial visibility timing, demo-only sources, resets, validation and CLI routing. Twenty-one actual Cairo renders cover all title/effect boundaries at480/720/800, plus a full39s GIF. Subsequently deployed to the target Pi:78 tests passed,44-second monitoring observed all six phases and a loop restart, and960×480/~62.825Hz was preserved. Physical panel edges and camera acceptance still requireon-site observation. See the project's self-contained deployment guide.

## v0.6.1 split introduction screens

During each3s introduction, the left panel exclusively presents the TEKGROAML wordmark, use-case icon and brand tagline. The right panel presents the application title/subtitle, both panels' metric roles and the countdown, without duplicating the icon/brand page. All three10s effect renders are pixel-identical to the previous implementation; the39s loop, simulated data and display signal are unchanged.
