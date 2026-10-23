"""Verify live input freshness, invalid input handling and timed waveform sampling."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gauges.common import Telemetry, TelemetrySource
from gauges.industrial_panel import IndustrialPanel

VALUES = {'speed': 68, 'rpm': 2400, 'temperature': 68.5, 'pressure': 4.2, 'voltage': 13.8, 'signal': .25}


class TelemetryTests(unittest.TestCase):
    def test_invalid_data_keeps_last_values_without_switching_to_simulation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.json'; path.write_text(json.dumps(VALUES))
            source = TelemetrySource(path)
            first = source.read(0); self.assertFalse(first.stale); self.assertFalse(first.simulated)
            path.write_text('{"speed":NaN}')
            failed = source.read(1)
            self.assertTrue(failed.stale); self.assertEqual(failed.speed, 68); self.assertFalse(failed.simulated)
            path.write_text(json.dumps(VALUES)); os.utime(path, (time.time()-5, time.time()-5))
            self.assertTrue(source.read(2).stale)
            os.utime(path, None); self.assertFalse(source.read(3).stale)

    def test_missing_file_never_produces_fake_live_telemetry(self):
        data = TelemetrySource(Path('/nonexistent/telemetry.json')).read(0)
        self.assertTrue(data.stale); self.assertFalse(data.simulated); self.assertEqual(data.speed, 0)

    def test_waveform_sample_rate_independent_of_rendering_fps(self):
        for fps in (15, 30, 60, 120):
            panel = IndustrialPanel(); data = Telemetry(signal=.5)
            for _ in range(fps): panel.update(1/fps, data)
            self.assertEqual(list(panel.history).count(.5), 30)
        panel.update(1/30, Telemetry(stale=True)); self.assertIsNone(panel.history[-1])


if __name__ == '__main__': unittest.main()
