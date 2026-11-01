"""Dual-round PC-case monitoring display; the monitored computer supplies live data."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('pc-monitor','PC case CPU/GPU and cooling display',('round','round'),'pc-monitor-sbs',
                      ('cpu-memory','gpu-cooling'),
                      ('scenes.different.pc_monitor.panels:CpuPanel','scenes.different.pc_monitor.panels:GpuPanel'),
                      'scenes.different.pc_monitor.model:PcDemo',live_factory='scenes.different.pc_monitor.model:PcJsonSource',
                      native_dual480=True)
