# Changelog

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
