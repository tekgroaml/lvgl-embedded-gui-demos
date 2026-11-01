# Changelog

## 0.10.0 — 2026-11-01 (same/different grouping and square same-content use cases)

- Organize canonical applications under scenes/same/{round,square} and scenes/different; organize four independent showcase scripts under demos/{same,different}/{round,square}.
- Extract shared CLI, timeline, scene selection and intro components into demos/shared. Same-content code no longer imports different-content businesses.
- Add square-specific retail promotions, meeting-room availability and parcel pickup applications, with separate3s brand/use-case introductions and10s effects;39s loop. Round same-content retains music, lighting and clock.
- Provide explicit clone/SBS square layouts at480/720/800 and60Hz, with no inferred square hardware refresh rate. Keep all existing view/layout IDs and legacy import/command adapters.
- Add grouped architecture/compatibility/business/raster tests, complete installation/SSH instructions and square39s preview. This release is local-only; no Pi connection, update or launch while displays are disconnected.

## 0.9.0 — 2026-11-01 (vivid same-content product showcase)

- Add ambient-light and ambient-clock, each with clone and SBS profiles. Time/weather/lighting are simulated; no audio or network integration.
- Give music-ambient a brighter saturated palette and neon spectrum. Share drawing helpers in common/neon.py.
- Add demos/same/round:3s identical introductions +10s effects per use case,39s loop; default hardware clone or explicit --signal sbs.
- Reuse timeline, scene factories, standard lifecycle and raster duplication. Preserve different-content commands and playlists.
- Add motion, contract, rollover, color and raster checks, two-topology renders, previews and installation instructions.

## 0.8.1 — 2026-11-01 (hardware-cloned dual-round input)

- Add music-ambient-clone for boards that duplicate one square input in hardware; preserve the observed480×480@62.811001Hz signal.
- Distinguish single-link-clone from double-width single-link-dual layouts, with explicit topology/refresh/profile declarations and geometry validation.
- Draw the shared clone rectangle once to avoid compositing circular edges twice. Keep SBS same-content and all different-content mappings.
- Add clone contract and actual raster tests;104 tests pass with Cairo.

## 0.8.0 — 2026-11-01 (local-only dual-round music and ambient lighting)

- Add music-ambient:64 radial simulated bands,112 BPM beat envelopes, breathing halos, color transitions and sample track progress; no audio capture or playback.
- Declare content modes per scene and layout. Only the new music view accepts --content same; existing commands and both39s playlists remain different-content.
- Render one circular raster tile and copy it to both SBS regions for pixel-identical software frames. Retain480/720/800 layouts and existing signal checks.
- Add local previews, standalone installation/SSH instructions, model/contract/raster tests and renderer regression checks. No new Pi runtime dependency.
- Implemented and validated on the Mac only; not deployed to or started on the Raspberry Pi. Physical music-scene acceptance is pending.

## 0.7.0 — 2026-11-01 (dual-square product showcase)

- Add square smart-home climate/energy and PC-case CPU/GPU dashboards; reuse the existing pump-station scene for the third use case.
- Add demos/different/square with its own playlist:3s distinct brand/application introductions +10s effects,39s loop. Keep round defaults and the original round playlist.
- Share timing, title roles, icons, scene factories, PC thermal simulation and square drawing helpers; no new runtime dependency.
- Add explicit --shape square to the common showcase wrapper, separate standard scene commands, bounded histories and energy-balance checks.
- Accept the observed960×480~62.825Hz input in square480 layouts without changing signals; industrial480 mapping moves to1.1.0. Stop old instances before upgrading.

## 0.6.1 — 2026-11-01 (distinct branding and application introduction panels)

- Split each3s intro into a left brand/icon screen and a right application-description screen, explicitly demonstrating two different displays.
- Keep all three10s effect pages pixel-identical, with unchanged playlist timing,39s loop and simulated data.
- Regenerate intro/loop previews and add presentation-role regression coverage.

## 0.6.0 — 2026-11-01 (product-use-case showcase)

- Add an independent demos/different/round directory with editable playlist, native vector icons/copy cards and standard-command wrapper.
- Loop flight instruments, car/motorcycle instrument use case and PC-case monitoring:3s title card +10s simulated effect each,39s total.
- Reuse scene model/panel factories inside one leased GTK surface, without subprocess/window switching or desktop gaps by design.
- Start the title clock after the first visible ready frame; keep presentation wall time independent of global demo_speed and prewarm effects to informative active states.
- Include status-visible stage/phase, playlist configuration digest, validation, previews and regression tests. Physical/camera acceptance remains pending.

## 0.5.0 — 2026-11-01 (PC-case monitoring scene)

- Add dual-round PC-monitor CPU/RAM and GPU/cooling pages, with480/720/800 layouts and native~62.825Hz acceptance on the480 layout.
- Model idle, CPU rendering, gaming and cooling with correlated power, thermal inertia, fan response and bounded memory/VRAM usage.
- Add explicit timestamped monitored-PC JSON input. Missing sensors remain unavailable; stale/invalid uploads never turn into synthetic data or local Pi measurements.
- Extract shared bounded regular-file snapshot reading, preserving the existing mixed-scene protocol.
- Include an optional Windows PowerShell CPU/RAM and available NVIDIA collector, with atomic local output and optional SSH-key-based Pi transfer. No Windows/NVIDIA runtime acceptance is claimed.
- Preserve the existing native Python/GTK/Cairo dependency set and standard command/lifecycle interface.

## 0.4.0 — 2026-11-01 (dual-round automotive and scene modules)

- Add automotive view with dedicated round speed/RPM/gear/trip and engine/fuel/voltage/oil-pressure panels.
- Link simulated driving phases, gears, RPM, load, thermal lag, fuel consumption and distance; demo only, no OBD or vehicle control.
- Accept60Hz and the observed~62.825Hz input in automotive-sbs-480 without changing display timing; add720/800 layouts.
- Split all four scenarios into scenes/<id>/ with declarations, models, panels and scene-owned layouts.
- Extract common drawing/theme/components, telemetry and simulation helpers; standard worker uses declarative scene factories instead of scene-name branches.
- Preserve legacy gauges imports, Pygame paths, existing public commands and layout IDs. Derive missing view from the explicit layout so two dual-round scenes are unambiguous.
- Generate manifest capabilities from the scene registry and retain independent deployment/SSH instructions.
- Keep live initialization free of simulated placeholders and retain old mixed-scene JSON behavior.

## 0.3.1 — 2026-11-01 (dual480 native input acceptance)

- Accept the observed960×480 native dual-round input at~62.825226Hz alongside60Hz in flight-sbs-480 layout v1.1.0; keep other layout timing lists unchanged.
- Validate accepted refresh lists explicitly and preserve the existing HDMI signal; no EDID/timing changes or forced60Hz.
- Deploy the native flight demo to HDMI-A-1 and confirm actual surface/viewport binding; physical panel observations remain separately recorded.
- Add native-rate regression checks and observed EDID/desktop diagnostics to deployment/verification documentation.

## 0.3.0 — 2026-10-25 (dual-round and dual-square scenes)

- Add dedicated dual-round flight instruments: attitude/heading and airspeed/altitude/VSI.
- Add dedicated dual-square pump-station overview and correlated trend/condition display.
- Generate autonomous, deterministic scene data: smooth flight phases with consistent altitude/VSI and bank/heading; pump duty cycles with pressure/thermal inertia and integrated delivered volume.
- Add scene-specific exact profiles and flight/industrial 480/720/800 SBS layouts; retain the original mixed automotive-industrial and live JSON behavior.
- Keep new scenarios explicitly demo-only; add optional demo_speed business configuration and a shared simulation clock independent of render FPS.
- Preserve the native Python/GTK/Cairo dependency set and standard ./app lifecycle.

## 0.2.0 — 2026-10-25 (native standard-interface preview)

- Add ./app info/check/run/start/status/logs/restart/stop with versioned manifest and exact dual-panel profile.
- Reuse automotive and industrial view logic through native GTK3/Cairo; no browser, Pygame, pip or virtual environment is required by the standard path.
- Add explicit 480/720/800 SBS software layouts with mode/geometry/version checks and no hardware auto-matching claims.
- Bind one full-canvas surface to a verified HDMI output; share connector ownership protocol with the round-screen app while retaining an independent repository.
- Supervise background lifecycle, idempotent startup, own-app replacement rollback and private ownership-checked control.
- Separate demo from live JSON, keep stale live data visibly stale, perform file reads off the GTK thread and reject blocking special files.
- Install missing native distribution dependencies only; retain optional legacy Pygame path behind --legacy-pygame.
- Add bilingual self-contained deployment/SSH documentation, software regression tests and actual Cairo offscreen renders.
- Physical dual-panel driver-board splitting and native on-screen acceptance remain pending.
