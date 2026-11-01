"""Reuse PC thermal/load simulation; no second implementation or host sensors."""
from scenes.pc_monitor.model import PcDemo


class PcSquareDemo(PcDemo):
    """Scene-owned demo factory sharing the existing PC dynamics."""
