# Telemetry protocol and legacy Pygame path

This reference preserves the data contract. Native ./app live mode selects input_file through examples/live.json; ./run.sh examples below belong to the optional legacy Pygame path.

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
