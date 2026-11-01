"""Square PC panels have their own geometry and retain the shared PC model."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('pc-monitor-square','Square PC hardware monitor',('square','square'),
                      'pc-monitor-square-sbs',('pc-system','pc-cooling'),
                      ('scenes.pc_monitor_square.panels:SystemPanel','scenes.pc_monitor_square.panels:CoolingPanel'),
                      'scenes.pc_monitor_square.model:PcSquareDemo',native_dual480=True)
